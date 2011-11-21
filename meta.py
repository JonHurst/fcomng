#!/usr/bin/python
# coding=utf-8

from globals import *
import cPickle as pickle
import re

class DU:

    def __init__(self,  data_filename, mu_filename, parent_sid, title, groupid, revdate):
        global g_paths
        self.data_filename = data_filename
        self.parent_sid = parent_sid
        self.title = title
        self.groupid = groupid
        self.revdate = revdate
        #parse metadata file
        e = et.ElementTree(None, g_paths.mus + mu_filename)
        if data_filename:
            self.msns = self.__get_msns__(e)
        self.tdu = False
        if e.getroot().attrib["tdu"] == "true":
            self.tdu = True
        self.linked_du = e.getroot().attrib["linked-du-ident"]
        self.affected_by = None
        self.revs = []
        for r in e.findall("revisions/content-revisions/rev-marks/rev"):
            path = r.attrib["path"]
            if path == "/": continue
            self.revs.append(path)
        self.revs.sort()


    def __get_msns__(self, e):
        m = e.find("effect").find("aircraft-ranges").find("effact").find("aircraft-range")
        if not et.iselement(m):
            msns = None
        else:
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


    def set_msns(self, msnlist):
        self.msns = msnlist


class FCOMMeta:

    class Section:

        def __init__(self, title, npid):
            self.title = title
            self.children = []
            self.du_list = []
            self.id = npid


        def add_child(self, sid):
            self.children.append(sid)


        def add_du(self, du_filename_tuple):
            self.du_list.append(du_filename_tuple)


    class Group:

        def __init__(self, title):
            self.title = title
            self.duids = []


        def add_duid(self, duid):
            self.duids.append(duid)


    class Aircraft:

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




    class RevisionRecord:

        def __init__(self, revclass, change, anchor):
            self.revclass = revclass
            self.change = change
            self.anchor = anchor


        def __str__(self):
            return "Class: %s Change: %s Anchor: %s" % (
                self.revclass,
                self.change,
                self.anchor)


    def __init__(self):
        global g_paths
        self.sections = {}
        self.dus = {}
        #optimisation: creatin DU instances requires parsing of thousands of m_data files, which is very slow;
        # we pickle the resulting data structure and only parse these files if the pickle file doesn't exist.
        du_pickle_path = g_paths.pickles + "dus"
        dus_from_pickle = False
        if os.path.exists(du_pickle_path):
            du_pickles = open(du_pickle_path)
            self.dus = pickle.Unpickler(du_pickles).load()
            dus_from_pickle = True
        self.groups = {}
        self.top_level_sids = []
        self.revdict = {}
        print "Scanning metadata"
        self.control = et.ElementTree(None, g_paths.control)
        self.global_meta = et. ElementTree(None, g_paths.global_meta)
        self.__build_revdict__(self.global_meta.find("revisions"))
        self.aircraft = self.Aircraft(self.global_meta.find("aat"))
        for psl in self.control.getroot().findall("psl"):
            print "Scanning", psl.attrib["pslcode"]
            self.top_level_sids.append((psl.attrib["pslcode"],))
            self.__process_psl__(psl, ())
        #optimisation
        if not dus_from_pickle:
            du_pickles = open(du_pickle_path, "w")
            pickle.Pickler(du_pickles).dump(self.dus)

    def __process_psl__(self, elem, sec_id):
        i = sec_id + (elem.attrib["pslcode"],)
        self.sections[i] = []
        section = self.Section(elem.findtext("title"), elem.attrib["id"])
        self.sections[i] = section
        if self.sections.has_key(i[:-1]):
            self.sections[i[:-1]].add_child(i)
        for e in elem:
            if e.tag == "du-inv":
                self.__process_duinv__(e, i)
            elif e.tag == "group":
                self.__process_group__(e, i)
            elif e.tag == "psl":
                self.__process_psl__(e, i)


    def __process_duinv__(self, elem, sec_id, groupid=None):
        global g_paths
        duids = []
        msnlist = []
        for s in elem.findall("du-sol"):
            data_file = os.path.basename(s.find("sol-content-ref").attrib["href"])
            meta_file = os.path.basename(s.find("sol-mdata-ref").attrib["href"])
            title = elem.find("title").text
            revdate = s.find("sol-content-ref").attrib["revdate"]
            #find duid - unfortunately only available in du file as root element code
            s = open(g_paths.dus + data_file).read(200)
            duid = s[s.find("code="):][6:22]
            #optimisation: if we have loaded self.dus from pickle, we will already have the
            #data and don't need to parse the MU file
            if not self.dus.has_key(duid):
                self.dus[duid] = DU(data_file, meta_file, sec_id, title, groupid, revdate)
            msns = self.dus[duid].msns
            if msns:
                msnlist.extend(msns)
            duids.append(duid)
            if groupid:
                self.groups[groupid].add_duid(duid)
        #we may have to create a fake du if we have a set if dus that only cover part of the fleet
        if msnlist:
            nc = self.notcovered(msnlist)
            if nc:
                duid = duid.split(".")[0] + ".NA"
                self.dus[duid] = DU("", meta_file, sec_id, title, groupid, "N/A")
                self.dus[duid].set_msns(nc)
                duids.append(duid)
        self.sections[sec_id].add_du(tuple(duids))


    def __process_group__(self, elem, sec_id):
        #note: groups don't nest, and they only contain du-inv sections
        groupid = elem.attrib["id"]
        self.groups[groupid] = self.Group(elem.find("title").text)
        for s in elem.findall("du-inv"):
            self.__process_duinv__(s, sec_id, groupid)


    def __build_revdict__(self, rev_elem):
        content_revisions = rev_elem.find("content-revisions")
        highlights = content_revisions.find("highlights")
        rev_marks = content_revisions.find("rev-marks")
        path_reo = re.compile(r"//([^\[]*)[^']*'([^']*)")
        for rev in rev_marks.findall("rev"):
            mo = path_reo.match(rev.attrib["path"])
            if not mo: print "regexp error"; continue
            change = rev.attrib["chg"]
            if change == "E": continue #not interested if only change is aircraft affected
            self.revdict[mo.group(2)] = self.RevisionRecord(
                mo.group(1),
                change,
                True if rev.attrib["anchor"] == "true" else False)



    def get_title(self, sid):
        return self.sections[sid].title


    def get_du_title(self, duid):
        return self.dus[duid].title


    def get_du_parent(self, duid):
        return self.dus[duid].parent_sid


    def get_du_group(self, duid):
        return self.dus[duid].groupid


    def get_du_filename(self, duid):
        return self.dus[duid].data_filename
    def get_du_revdate(self, duid):
        return self.dus[duid].revdate


    def get_du_revs(self, duid):
        return self.dus[duid].revs


    def get_group_title(self, groupid):
        return self.groups[groupid].title


    def get_dus(self, sid):
        return self.sections[sid].du_list


    def get_children(self, sid):
        return self.sections[sid].children


    def get_all_sids(self):
        retval = []
        for s in self.top_level_sids:
            retval.append(s)
            retval += self.get_descendants(s)
        return retval


    def get_descendants(self, sid):
        retval = []
        for c in self.get_children(sid):
            retval.append(c)
            retval += self.get_descendants(c)
        return retval


    def get_leaves(self, prune=3):
        retval = []
        for s in self.get_all_sids():
            if len(s) > prune: continue
            if len(s) == prune or not self.get_children(s):
                retval.append(s)
        return retval


    def get_npid(self, sid):
        return self.sections[sid].id


    def get_fleet(self):
        return [(X, self.aircraft.aircraft[X]) for X in self.aircraft.aircraft]


    def affected(self, msn, du_filename):
        ac_list = self.dus[du_filename].msns
        if not ac_list or msn in ac_list:
            return True
        return False


    def applies(self, duid):
        return self.dus[duid].msns


    def notcovered(self, msnlist):
        return list(set(self.aircraft.all()) - set(msnlist))


    def applies_string(self, msnlist):
        return self.aircraft.applies_string(msnlist)



    def is_tdu(self, duid):
        return self.dus[duid].tdu


    def get_revision_code(self, ident):
        if self.revdict.has_key(ident):
            return self.revdict[ident].change
        return None


    def dump(self):
        print "Sections:\n==========\n"
        for s in self.get_all_sids():
            section = self.sections[s]
            indent = " " * ((len(s) - 1) * 4)
            print indent, ".".join(s), ": ", section.title
            for du in self.get_dus(s):
                print indent, " ", du
        print "DUs:\n============\n"
        for du in sorted(self.dus):
            print du, self.dus[du].parent_sid, self.dus[du].msns, self.dus[du].tdu
        print "\n\nLeaves:\n=======\n"
        for l in self.get_leaves():
            print ".".join(l), ": ", self.get_title(l)
        print "\n\nAircraft:\n=========\n"
        self.aircraft.dump()
        print "\n\nAircraft list test\n"
        print self.affected("4556", "00000284.0003001")
        print self.applies("00000284.0003001")
        print self.applies("00000879.0004001")
        print "\n\nGroups\n===========\n"
        for k in sorted(self.groups):
            print k, self.groups[k].duids


