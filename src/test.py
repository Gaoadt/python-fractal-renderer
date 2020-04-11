class Obj:
    lst = []
    v1 = 1

obj1 = Obj()
obj2 = Obj()
obj1.lst.append("ui")
obj1.v1 = 2
print(obj1.lst)
print(obj2.lst)

print(obj1.v1)
print(obj2.v1)