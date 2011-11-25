#!/usr/bin/python
# coding=utf-8

"""\
This module encapsulates the meta data for an Airbus manual.

There are three sources for the metadata. The paths to these sources
are available in the global variable g_paths which is populated from
the 'Start.xml' file in the root of the XML data.

g_paths.control is the source for the structure of the manual. The
main structural components of the document are sections, groups,
du_containers and dus. In the file, the top level element (<product>)
contains a number of sections (<psl>). Each section may contain other
sections xor a mixture of groups (<group>) and du_containers
(<du-inv>). A group only contains du_containers and neither groups nor
du_containers can nest. The effect is a tree of section nodes with
content node leaves, i.e. there is no content above the lowest level
of the hierarchy. Groups appear to be a syntactic hint to not display
individual DU titles, instead displaying the single group title for
all the contained DUs. Indexes should also point at the group and omit
the contained DUs. The du_containers each reference one or more
'solutions' (<du-sol>), a solution being a pair of file references,
one to a DU file and the other to its accompanying DU metadata file
(see below). If multiple solutions are referenced, each solution
pertains to a subsection of the fleet.

The <product> element of g_paths.control also contains the manual name
and a revdate that can be used to describe the version of the whole
manual.

g_paths.global_meta contains a list linking aircraft registration,
type and msn and a list of revisions at section level.

Individual DU mdata files contain a list of msns that the paired DU is
applicable to and a list of revisions at DU level. The root <dumdata>
file also has the DU identity, whether it is a TDU and if it is a TDU,
the identity of the DU that it overrides.

To use the module, just create a FCOMMeta object after creating the
global g_paths object.

The main data structure used is a dictionary with identifiers as
keys. The identifier can be either a DU identifier
(e.g. '00001234.0000123'), a DU container identifier
(e.g. '00001234'), a group identifier (e.g. NG12345), a section
identifier (e.g. NP02699) or a section tuple (e.g. ('DSC', '22',
'40'). Each dictionary entry references an object with at least a
parentID attribute, a list of childID attributes and a title. Other
useful data is stored with this object as appropriate.

"""
from globals import *
import cPickle as pickle
import re

#enums
TYPE_DU, TYPE_DUCONTAINER, TYPE_GROUP, TYPE_SECTION = range(4)


class _Node:

    def __init__(self, parent, title):
        self.parent = parent
        self.children = []
        self.title = title


    def add_child(self, child_id):
        self.children.append(child_id)


class _DU(_Node):

    node_type = TYPE_DU

    def __init__(self, parent, title, data_filename, mu_filename, revdate):
        global g_paths
        _Node.__init__(self, parent, title)
        self.data_filename = data_filename
        self.revdate = revdate
        #parse metadata file
        e = et.ElementTree(None, g_paths.mus + mu_filename)
        #extract ident - this is the easiest place to get it from
        self.ident = e.getroot().attrib["code"]
        #extract aircraft applicability
        if data_filename:
            self.msns = self._get_msns(e)
        #extract tdu info
        self.tdu = True if e.getroot().attrib["tdu"] == "true" else False
        self.linked_du = e.getroot().attrib["linked-du-ident"]
        #extract revision info
        self.revs = []
        for r in e.findall("revisions/content-revisions/rev-marks/rev"):
            path = r.attrib["path"]
            if path == "/": continue
            if r.attrib["chg"][-1:] == "N": path += "/"
            self.revs.append(path + "/text()")
        self.revs.sort()


    def _get_msns(self, e):
        m = e.find("effect/aircraft-ranges/effact/aircraft-range")
        msns = None
        if et.iselement(m):
            msns = []
            for msn in m.text.split(" "):
                #supposition: a pair of numbers together indicates all aircraft with MSNs between
                #[:4] and [4:]
                if len(msn) == 8:
                    for rangemsn in range(int(msn[:4]), int(msn[4:]) + 1):
                        msns.append(str(rangemsn))
                else:
                    msns.append(msn)
        return msns


class _DU_Container(_Node):

    node_type = TYPE_DUCONTAINER

    def __init__(self, parent, title):
        _Node.__init__(self, parent, title)
        self.overridden_by = None


class _Section(_Node):

    node_type = TYPE_SECTION

    def __init__(self, parent, title, pslcode):
        _Node.__init__(self, parent, title)
        self.pslcode = pslcode


class _Group(_Node):
    node_type = TYPE_GROUP
    def __init__(self, parent, title):
        _Node.__init__(self, parent, title)



class _Aircraft:

    def __init__(self, aat):
        self.aircraft = {}
        self.fleets = {}
        self.pseudofleets = {}
        for a in aat.findall("aircraft-item"):
            if a.attrib["acn"]:
                self.aircraft[a.attrib["msn"]] = a.attrib["acn"]
                if not self.pseudofleets.has_key(a.attrib["acn"][:-1] + "*"):
                    self.pseudofleets[a.attrib["acn"][:-1] + "*"] = set()
                self.pseudofleets[a.attrib["acn"][:-1] + "*"].add(a.attrib["msn"])
            else:
                self.aircraft[a.attrib["msn"]] = a.attrib["msn"]
            m = a.attrib["aircraft-model"]
            if not self.fleets.has_key(m):
                self.fleets[m] = set()
            self.fleets[m].add(a.attrib["msn"])


    def applies_string(self, msnlist):
        msnset = set(msnlist)
        fleets = []
        for f in self.fleets.keys():
           if self.fleets[f] <= msnset:
                fleets.append(f + " fleet")
                msnset = msnset.difference(self.fleets[f])
        pseudofleets = []
        for p in self.pseudofleets.keys():
            if self.pseudofleets[p] <= msnset:
                pseudofleets.append(p)
                msnset = msnset.difference(self.pseudofleets[p])
        remaining = pseudofleets + [self.aircraft[X] for X in list(msnset)]
        remaining.sort()
        fleets.sort()
        return ", ".join(fleets + remaining)


    def msn_to_reg(self, msn):
        return self.aircraft[msn]


    def all(self):
        return self.aircraft


    def dump(self):
        for k in self.fleets.keys():
            print "\n", k, "fleet: "
            for a in self.fleets[k]:
                if self.aircraft[a]:
                    print self.aircraft[a]
                else:
                    print a


class _RevisionRecord:

    def __init__(self, revclass, change, anchor):
        self.revclass = revclass
        self.change = change
        self.anchor = anchor


    def __str__(self):
        return "Class: %s Change: %s Anchor: %s" % (
            self.revclass,
            self.change,
            self.anchor)



class FCOMMeta:


    def __init__(self, use_pickle=False):
        global g_paths
        print "Scanning metadata"
        if use_pickle:
            pickle_file = open(g_paths.pickles + "meta.pkl") #may throw IOError
            (self.revdict, self.aircraft, self.nodes) = pickle.load(pickle_file)
            pickle_file.close()
        else:
            self.global_meta = et. ElementTree(None, g_paths.global_meta)
            self.aircraft = _Aircraft(self.global_meta.find("aat"))
            self.revdict = {}
            self._build_revdict(self.global_meta.find("revisions"))
            self.nodes = {None: _Section(None, "", ())}
            self.control = et.ElementTree(None, g_paths.control)
            for psl in self.control.getroot().findall("psl"):
                print "Scanning", psl.attrib["pslcode"]
                self._process_psl(psl, None)
            pickle_file = open(g_paths.pickles + "meta.pkl", "w")
            pickle.dump((self.revdict, self.aircraft, self.nodes), pickle_file)
            pickle_file.close()


    def _process_psl(self, elem, parent_id):
        pslcode = self.nodes[parent_id].pslcode + (elem.attrib["pslcode"],)
        #create and link up new section
        section = _Section(parent_id, elem.findtext("title"), pslcode)
        ident = elem.attrib["id"]
        self.nodes[ident] = section
        self.nodes[pslcode] = section
        self.nodes[parent_id].add_child(ident)
        #process section
        for e in elem:
            if e.tag == "du-inv":
                self._process_duinv(e, ident)
            elif e.tag == "group":
                self._process_group(e, ident)
            elif e.tag == "psl":
                self._process_psl(e, ident)


    def _process_duinv(self, elem, parent_id):
        global g_paths
        #create and link up new DU container
        container = _DU_Container(parent_id, elem.find("title").text)
        container_id = elem.attrib["code"]
        self.nodes[container_id] = container
        self.nodes[parent_id].add_child(container_id)
        #process each solution
        msnlist = []
        for s in elem.findall("du-sol"):
            #extract relevant data from XML
            data_file = os.path.basename(s.find("sol-content-ref").attrib["href"])
            meta_file = os.path.basename(s.find("sol-mdata-ref").attrib["href"])
            title = elem.find("title").text
            revdate = s.find("sol-content-ref").attrib["revdate"]
            #create and link the new DU
            du = _DU(container_id, title, data_file, meta_file, revdate)
            duid = du.ident
            self.nodes[duid] = du
            container.add_child(duid)
            #check for TDU status and update relevant container if set
            if du.tdu and du.linked_du: self.nodes[du.linked_du].overridden_by = duid
            #the DU self populates with an msn list on creation; use this to add to total coverage list
            msns = du.msns
            if msns: msnlist.extend(msns)
        #we may have to create a fake du if we have a set if dus that only cover part of the fleet
        if msnlist: #msnlist will be None or a list containing the entire fleet if the entire fleet is covered
            nc = self.notcovered(msnlist)
            if nc:
                duid = container_id + ".NA"
                self.nodes[duid] = _DU(container_id, title, "", meta_file, "N/A")
                self.nodes[duid].msns = nc
                container.add_child(duid)


    def _process_group(self, elem, parent_id):
        #note: groups don't nest, and they only contain du-inv sections
        groupid = elem.attrib["id"]
        self.nodes[groupid] = _Group(parent_id, elem.find("title").text)
        self.nodes[parent_id].add_child(groupid)
        for s in elem.findall("du-inv"):
            self._process_duinv(s, groupid)


    def _build_revdict(self, rev_elem):
        rev_marks = rev_elem.find("content-revisions/rev-marks")
        #path is of th form //du-sol[@code='00002261.0003001']
        #group(1) is the node type, group(2) is the ident
        path_reo = re.compile(r"//([^\[]*)[^']*'([^']*)")
        for rev in rev_marks.findall("rev"):
            mo = path_reo.match(rev.attrib["path"])
            if not mo: print "regexp error"; continue
            change = rev.attrib["chg"]
            if change == "E": continue #not interested if only change is aircraft affected
            self.revdict[mo.group(2)] = _RevisionRecord(
                mo.group(1),
                change,
                True if rev.attrib["anchor"] == "true" else False)





    def get_fleet(self):
        return [(X, self.aircraft.aircraft[X]) for X in self.aircraft.aircraft]


    def applies(self, duid):
        return self.nodes[duid].msns


    def notcovered(self, msnlist):
        return list(set(self.aircraft.all()) - set(msnlist))


    def applies_string(self, msnlist):
        return self.aircraft.applies_string(msnlist)


    def _dump_element(self, ident, spaces):
        if isinstance(self.nodes[ident], _DU) and self.nodes[ident].tdu:
            print "+" * 20
        elif isinstance(self.nodes[ident], _DU_Container) and self.nodes[ident].overridden_by:
            print "-" * 10, "Overridden by", self.nodes[ident].overridden_by
        print spaces, ident, self.nodes[ident].node_type, self.nodes[ident].title
        for c in self.nodes[ident].children:
            self._dump_element(c, spaces + "  ")

    def dump(self):
        self._dump_element(None, "")


    def get_title(self, ident):
        return self.nodes[ident].title


    def get_children(self, ident):
        return tuple(self.nodes[ident].children)


    def get_type(self, ident):
        return self.nodes[ident].node_type


    def get_pslcode(self, ident):
        return self.nodes[ident].pslcode


    def get_root_nodes(self):
        return self.nodes[None].children


    def get_filename(self, ident):
        return self.nodes[ident].data_filename


    def get_revdate(self, ident):
        return self.nodes[ident].revdate


    def get_parent(self, ident):
        return self.nodes[ident].parent


    def get_revision_code(self, ident):
        r =  self.revdict.get(ident)
        return None if not r else r.change

    def get_du_revs(self, ident):
        return self.nodes[ident].revs


    def get_overriding(self, ident):
        return self.nodes[ident].overridden_by


    def is_valid(self, ident):
        return ident in self.nodes


    def is_tdu(self, ident):
        return self.nodes[ident].tdu


    def get_ancestors(self, ident):
        ancestors = []
        ident = self.nodes[ident].parent
        while ident:
            ancestors.insert(0, ident)
            ident = self.nodes[ident].parent
        return ancestors


if __name__ == "__main__":
    global g_paths
    import sys
    if len(sys.argv) != 2:
        print "Usage: ", sys.argv[0], "start_file"
        sys.exit(1)
    g_paths.initialise(*sys.argv + ["."])
    fcm = FCOMMeta()
    fcm.dump()

