import process
import re

fcomchanges_file = "fcomchanges-201110"

fcm = process.FCOMMeta(process.control_file)
outstr = ""
onlyin = re.compile("Only in ([^:]*): (.*)")
differ = re.compile("Files ([^ ]*)")
for line in file(fcomchanges_file):
    mo = onlyin.search(line)
    if mo:
        try:
            parent = fcm.get_du_parent("./DU/" + mo.group(2))
        except:
            parent = None
        if parent:
            outstr += "<li><a href='%s'>New DU</a></li>\n" % (
                ".".join(parent[:3]) + ".html#duid" + mo.group(2).split(".")[0]
                )
        continue

    mo = differ.search(line)
    if mo:
        filename = mo.group(1).split("/")[-1]
        parent = fcm.get_du_parent("./DU/" + filename)
        outstr += "<li><a href='%s'>DU Changed</a></li>\n" % (
            ".".join(parent[:3]) + ".html#duid" + filename.split(".")[0]
            )


print "<html><head></head><body><ul>\n" + outstr + "</ul></body></html>"
