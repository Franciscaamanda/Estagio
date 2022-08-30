import xml.etree.ElementTree as et

tree = et.parse("515_20210809_13731645.xml")
root = tree.getroot()

#for child in root:
#    for attrib in child.attrib:
#        print(attrib + "\n")
#    print(child.tag)

for filhos in root.iter():
    print(filhos)

#for textos in root.itertext():
#    print(textos)
    #print(filhos.)

texto = root.findtext('./article/body/Texto')
print(texto)

