from struct import pack, unpack

class TAG:
    def __init__(self,name,ID,/):
        self.ID = ID
        self.name = name
    def write_prefix(self,file,/):
        file.write(pack('>bh%ss'%len(self.name),self.ID,len(self.name),bytes(self.name,'utf-8')))
    def write_infix(self,file,/):
        raise NotImplementedError
    def write_postfix(self,file,/):
        raise NotImplementedError
    def write(self,file,/):
        self.write_prefix(file)
        self.write_infix(file)
        self.write_postfix(file)

class TAG_Number(TAG):
    format_char = {
        1:'b',
        2:'h',
        3:'i',
        4:'q',
        5:'f',
        6:'d'
    }
    def __init__(self,name,ID,value,/):
        super().__init__(name,ID)
        self.value = value
    def write_infix(self,file,/):
        file.write(pack('>%s'%TAG_Number.format_char[self.ID],self.value))
    def write_postfix(self,file,/):
        pass

class TAG_Number_Array(TAG):
    format_char = {
        7:'b',
        11:'i',
        12:'q'
    }
    def __init__(self,name,ID,value,/):
        super().__init__(name,ID)
        self.value = []
    def write_infix(self,file,/):
        file.write(pack('>i%s%s' % (len(self.value),TAG_Number_Array.format_char[self.ID]), self.value))
    def write_postfix(self,file,/):
        pass
    @property
    def values(self,/):
        return self.value
    @values.setter
    def values(self,value,/):
        self.value = value

class TAG_End:
    ID = 0
    @staticmethod
    def write(file,/):
        file.write(b'\x00')

class TAG_Byte(TAG_Number):
    ID = 1
    def __init__(self,name,value,/):
        super().__init__(name,1,value)

class TAG_Short(TAG_Number):
    ID = 2
    def __init__(self,name,value,/):
        super().__init__(name,2,value)

class TAG_Int(TAG_Number):
    ID = 3
    def __init__(self,name,value,/):
        super().__init__(name,3,value)

class TAG_Long(TAG_Number):
    ID = 4
    def __init__(self,name,value,/):
        super().__init__(name,4,value)

class TAG_Float(TAG_Number):
    ID = 5
    def __init__(self,name,value,/):
        super().__init__(name,5,value)

class TAG_Double(TAG_Number):
    ID = 6
    def __init__(self,name,value,/):
        super().__init__(name,6,value)

class TAG_Byte_Array(TAG_Number_Array):
    ID = 7
    def __init__(self,name,values,/):
        super().__init__(name,7,values)

class TAG_String(TAG):
    ID = 8
    def __init__(self,name,value,/):
        super().__init__(name,8)
        self.value = value
    def write_infix(self,file,/):
        file.write(pack('>h%ss'%len(self.value),len(self.value),bytes(self.value,'utf-8')))
    def write_postfix(self,file,/):
        pass

class TAG_List(TAG):
    ID = 9
    def __init__(self,name,cls,values,/):
        super().__init__(name,9)
        self.value = values
        self.cls = cls
    def write_infix(self,file,/):
        file.write(pack('>bi',self.cls.ID,len(self.value)))
        for tag in self.value:
            tag.write_infix(file)
    def write_postfix(self,file,/):
        pass
    @property
    def values(self,/):
        return self.value
    @values.setter
    def values(self,value,/):
        self.value = value

class TAG_Compound(TAG):
    ID = 10
    def __init__(self,name,tags,/):
        super().__init__(name,10)
        self.value = tags
    def write_infix(self,file,/):
        for tag in self.value:
            tag.write(file)
        TAG_End.write(file)
    @property
    def values(self,/):
        return self.value
    @values.setter
    def values(self,value,/):
        self.value = value
    @property
    def tags(self,/):
        return self.value
    @tags.setter
    def tags(self,value,/):
        self.value = value

class TAG_Int_Array(TAG_Number_Array):
    ID = 11
    def __init__(self,name,values,/):
        super().__init__(name,11,values)

class TAG_Long_Array(TAG_Number_Array):
    ID = 12
    def __init__(self,name,values,/):
        super().__init__(name,12,values)