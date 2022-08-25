
#===========================




def PrintViewA(obj, fileName):
  viewFile = open(fileName, "a")
  if viewFile:
    viewFile.write(str(obj)+"\n")
    viewFile.close()
    
def PrintViewB(obj, fileName):
  viewFile = open(fileName, "a")
  if viewFile:
    viewFile.write(str(obj))
    viewFile.close()    

#===========================

