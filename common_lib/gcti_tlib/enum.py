#
#                  === Enumeration ===
#
#

#================ Enum ===================

class EnumElem:
  """Enumeration element - is a pair of: name and val
  
  On printing, and in string operations it yields name - string.
  In other operations                   it yields val  - integer.
  """
  
  def __init__(self, name, val):
    self.name = name
    self.val = val
    

  def __repr__(self):
    return self.name
    

  def __str__(self):
    return self.name


  def __coerce__(self, other):
    if type(self) == type(other):
      return (self.val, other.val)
    else: 
      if type(other) == type(""):
        return (self.name, other)
      else:  
        return (self.val, other) 


class Enum: 
  """ Enumeration
  
  Enumeration is a set of EnumElem.   
  All enumeration members are in self.members.
  At the same time every enumeration member may be accessed by name, if:
    colors = Enum("White, Black, Green")
  then
    colors.White == colors.member[0] 
    colors.Black == colors.member[1]
    colors.Green == colors.member[2]

    color.Black.name == "Black"
    color.Black == 1
  """

  def __init__(self, strMembers):
    """members is a string describing enumeration member in C-like stile:
    colors = Enum("White, Black, Green = 10, Red, Blue")
    """

    self.members = []

    val = 0
    for strMem in strMembers.split( ","):
      memDef = strMem.strip().split("=")
      assert len(memDef) in (1,2), "Bad enumeration definition %s" % strMem 
      name = memDef[0].strip()
      if   len(memDef) == 1:
        pass
      elif len(memDef) == 2:
        val = eval(memDef[1])
      
      mem = EnumElem(name, val)
      self.members.append(mem)
      setattr(self, name, mem)
      val = val+1


def ValToEnumElem(enum, val):
  """Convert val to enumeration element with the same val."""
  
  for obj in enum.members:
    if obj.val == val:
      return obj
    
  return None      


def NameToEnumElem(enum, name):
  """Convert name to enumeration element with the same name."""

  for obj in enum.members:
    if obj.name == name:
      return obj
    
  return None      


if 0: # Set 1 to test module
  print
  print "*** class Enum test ***"

  colors = Enum("White, Black, Green = 10, Red, Blue")
  print
  for c in colors.members:
    print "|"+c+"|"
 
  print
  print colors.White + 0
  print colors.Black + 0     
  print colors.Green + 0
  print colors.Red   + 0
  print colors.Blue  + 0
  print
  print colors.Green
  print `colors.Green`
  print str(colors.Green)
  print colors.Green + 5
  print colors.Green + colors.Red
  print (colors.Green)

  print 
  print ValToEnumElem(colors, 11)
