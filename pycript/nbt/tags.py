from struct import pack, unpack

class TAG:
    def __init__(self,name,ID,/):
        self.ID = ID
        self.name = name
    def write_prefix(self,file,/):
        file.write(pack('>bh%ss'%len(self.name),self.ID,len(self.name),bytes(self.name,'utf-8')))
    def write_infix(self,file,/):
        raise NotImplementedError
    def write(self,file,/):
        self.write_prefix(file)
        self.write_infix(file)

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

class TAG_Number_Array(TAG):
    format_char = {
        7:'b',
        11:'i',
        12:'q'
    }
    def __init__(self,name,ID,value,/):
        super().__init__(name,ID)
        self.value = value
    def write_infix(self,file,/):
        file.write(pack('>i',len(self.value)))
        f = TAG_Number_Array.format_char[self.ID]
        for value in self.value:
            file.write(pack(f'>{f}',value))
    @property
    def values(self,/):
        return self.value
    @values.setter
    def values(self,value,/):
        self.value = value

class TAG_End(TAG):
    ID = 0
    @staticmethod
    def write(file,/):
        file.write(b'\x00')
    @classmethod
    def write_infix(cls,file,/):
        cls.write(file)
    @staticmethod
    def write_prefix(file,/):
        pass

class TAG_Byte(TAG_Number):
    ID = 1
    def __init__(self,name,value,/):
        super().__init__(name,1,value)
    def __str__(self,/):
        return f'"{self.name}":{self.value}b'

class TAG_Short(TAG_Number):
    ID = 2
    def __init__(self,name,value,/):
        super().__init__(name,2,value)
    def __str__(self,/):
        return f'"{self.name}":{self.value}s'

class TAG_Int(TAG_Number):
    ID = 3
    def __init__(self,name,value,/):
        super().__init__(name,3,value)
    def __str__(self,/):
        return f'"{self.name}":{self.value}'

class TAG_Long(TAG_Number):
    ID = 4
    def __init__(self,name,value,/):
        super().__init__(name,4,value)
    def __str__(self,/):
        return f'"{self.name}":{self.value}L'

class TAG_Float(TAG_Number):
    ID = 5
    def __init__(self,name,value,/):
        super().__init__(name,5,value)
    def __str__(self,/):
        return f'"{self.name}":{self.value}f'

class TAG_Double(TAG_Number):
    ID = 6
    def __init__(self,name,value,/):
        super().__init__(name,6,value)
    def __str__(self,/):
        return f'"{self.name}":{self.value}d'

class TAG_Byte_Array(TAG_Number_Array):
    ID = 7
    def __init__(self,name,values,/):
        super().__init__(name,7,values)
    def __str__(self,/):
        return f'"{self.name}":[B;{",".join([str(_) for _ in self.value])}]'

class TAG_String(TAG):
    ID = 8
    def __init__(self,name,value,/):
        super().__init__(name,8)
        self.value = value
    def write_infix(self,file,/):
        file.write(pack('>h%ss'%len(self.value),len(self.value),bytes(self.value,'utf-8')))
    def __str__(self,/):
        return f'"{self.name}":"{self.value}"'

class TAG_List(TAG):
    EMPTY_LIST_TAG_END = True
    ID = 9
    class_guess = {
        int: TAG_Int,
        float: TAG_Float,
        str: TAG_String
    }
    def __init__(self,name,/,values=None,cls=None):
        super().__init__(name,9)
        self.value = values or []
        if cls is None:
            if len(self.value) > 0:
                cls = type(self.value[0])
            else:
                if TAG_List.EMPTY_LIST_TAG_END:
                    cls = TAG_End
                else:
                    raise TypeError("That isn't a valid type for TAG_List, or it couldn't be guessed.")
        if not issubclass(cls, TAG):
            if cls in TAG_List.class_guess:
                cls = TAG_List.class_guess[cls]
            else:
                if cls is list:
                    if len(self.value) > 0 and self.value[0] is int:
                        cls = TAG_Int_Array
                    else:
                        cls = TAG_List
                else:
                    raise TypeError("That isn't a valid type for TAG_List, or it couldn't be guessed.")
        self.cls = cls
    def write_infix(self,file,/):
        if TAG_List.EMPTY_LIST_TAG_END and len(self.value) == 0:
            file.write(pack('>bi',0,0))
        else:
            file.write(pack('>bi',self.cls.ID,len(self.value)))
            for tag in self.value:
                if isinstance(tag,TAG):
                    tag.write_infix(file)
                else:
                    t = self.cls(None,tag)
                    t.write_infix(file)
    @property
    def values(self,/):
        return self.value
    @values.setter
    def values(self,value,/):
        self.value = value
    def __str__(self,/):
        return f'"{self.name}":[{",".join([str(_) for _ in self.value])}]'

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
    def __str__(self,/):
        return f'"{self.name}":{{{",".join([str(_) for _ in self.value])}}}'

class TAG_Int_Array(TAG_Number_Array):
    ID = 11
    def __init__(self,name,values,/):
        super().__init__(name,11,values)
    def __str__(self,/):
        return f'"{self.name}":[I;{",".join([str(_) for _ in self.value])}]'

class TAG_Long_Array(TAG_Number_Array):
    ID = 12
    def __init__(self,name,values,/):
        super().__init__(name,12,values)
    def __str__(self,/):
        return f'"{self.name}":[L;{",".join([str(_) for _ in self.value])}]'

class NBT_File(TAG_Compound):
    def __init__(self,tags,/):
        super().__init__('root',tags)
    def write_prefix(self,file,/):
        file.write(b'\x0A\x00\x00')
    def __str__(self,/):
        return f'{{{",".join([str(_) for _ in self.value])}}}'