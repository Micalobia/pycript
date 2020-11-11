from struct import pack, unpack

class TAG:
    def __init__(self,name,ID,value,/):
        self.ID = ID
        self.name = name
        self.value = value
    def write_prefix(self,file,/):
        file.write(pack('>bh%ss'%len(self.name),self.ID,len(self.name),bytes(self.name,'utf-8')))
    def write_infix(self,file,/):
        raise NotImplementedError
    def write(self,file,/):
        self.write_prefix(file)
        self.write_infix(file)
    @staticmethod
    def read_prefix(file,/):
        ID = unpack('>b',file.read(1))[0]
        name_len = unpack('>h',file.read(2))[0]
        name = unpack('>%ss' % name_len, file.read(name_len))
        return (ID, name)
    @staticmethod
    def read_infix(file,/):
        raise NotImplementedError
    @classmethod
    def read(cls,file,/):
        ID, name = cls.read_prefix(file)
        value = cls.read_infix(file)
        return cls(name, ID, value)

class TAG_Number(TAG):
    def __init__(self,name,ID,value,/):
        super().__init__(name,ID,value)
    def write_infix(self,file,/):
        char = type(self).CHAR
        file.write(pack('>%s'%char,self.value))
    @staticmethod
    def read_infix(self,file,/):
        char = type(self).CHAR
        length = type(self).LENGTH
        return unpack('>%s'%char,file.read(length))

class TAG_Number_Array(TAG):
    def __init__(self,name,ID,values,/):
        super().__init__(name,ID,values)
    def write_infix(self,file,/):
        file.write(pack('>i',len(self.value)))
        char = type(self).CHAR
        for value in self.value:
            file.write(pack(f'>{char}',value))
    @classmethod
    def read_infix(cls,file,/):
        count = unpack('>i',file.read(4))
        char = cls.CHAR
        length = cls.LENGTH
        ret = []
        for _ in range(count):
            ret.append(unpack(f'>{char}',file.read(length)))
        return ret
    @property
    def values(self,/):
        return self.value
    @values.setter
    def values(self,value,/):
        self.value = value

class TAG_End(TAG):
    ID = 0
    def __init__(self,name = None,ID = None,value = None,/):
        pass
    @staticmethod
    def write(file,/):
        file.write(b'\x00')
    @classmethod
    def write_infix(cls,file,/):
        cls.write(file)
    @staticmethod
    def write_prefix(file,/):
        pass
    @staticmethod
    def read_prefix(file,/):
        pass
    @staticmethod
    def read_infix(file,/):
        pass
    @staticmethod
    def read(file,/):
        assert file.read(1) == b'\x00'
        return TAG_End()

class TAG_Byte(TAG_Number):
    ID = 1
    CHAR = 'b'
    LENGTH = 1
    def __init__(self,name,value,/):
        super().__init__(name,1,value)
    def __str__(self,/):
        return f'{self.name}:{self.value}b'

class TAG_Short(TAG_Number):
    ID = 2
    CHAR = 'h'
    LENGTH = 2
    def __init__(self,name,value,/):
        super().__init__(name,2,value)
    def __str__(self,/):
        return f'{self.name}:{self.value}s'

class TAG_Int(TAG_Number):
    ID = 3
    CHAR = 'i'
    LENGTH = 4
    def __init__(self,name,value,/):
        super().__init__(name,3,value)
    def __str__(self,/):
        return f'{self.name}:{self.value}'

class TAG_Long(TAG_Number):
    ID = 4
    CHAR = 'q'
    LENGTH = 8
    def __init__(self,name,value,/):
        super().__init__(name,4,value)
    def __str__(self,/):
        return f'{self.name}:{self.value}L'

class TAG_Float(TAG_Number):
    ID = 5
    CHAR = 'f'
    LENGTH = 4
    def __init__(self,name,value,/):
        super().__init__(name,5,value)
    def __str__(self,/):
        return f'{self.name}:{self.value}f'

class TAG_Double(TAG_Number):
    ID = 6
    CHAR = 'd'
    LENGTH = 8
    def __init__(self,name,value,/):
        super().__init__(name,6,value)
    def __str__(self,/):
        return f'{self.name}:{self.value}d'

class TAG_Byte_Array(TAG_Number_Array):
    ID = 7
    CHAR = 'b'
    LENGTH = 1
    def __init__(self,name,values,/):
        super().__init__(name,7,values)
    def __str__(self,/):
        return f'{self.name}:[B;{",".join([str(_) for _ in self.value])}]'

class TAG_String(TAG):
    ID = 8
    def __init__(self,name,value,/):
        super().__init__(name,8,value)
    def write_infix(self,file,/):
        file.write(pack('>h%ss'%len(self.value),len(self.value),bytes(self.value,'utf-8')))
    @staticmethod
    def read_infix(file,/):
        name_len = unpack('>h',file.read(2))
        name = unpack('>%ss' % name_len, file.read(name_len))
        return name
    def __str__(self,/):
        return f'{self.name}:"{self.value}"'

class TAG_List(TAG):
    EMPTY_LIST_TAG_END = True
    ID = 9
    class_guess = {
        int: TAG_Int,
        float: TAG_Float,
        str: TAG_String
    }
    def __init__(self,name,/,values=None,cls=None):
        super().__init__(name,9,values or [])
        if cls is None:
            if len(values) > 0:
                cls = type(values[0])
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
                    if len(values) > 0 and values[0] is int:
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
    @staticmethod
    def read_infix(file,/):
        ID = unpack('>b',file.read(1))
        cls = ID_Type[ID]
        size = unpack('>i',file.read(4))
        ret = []
        for i in range(size):
            ret.append(cls(None, cls.read_infix(file)))
        return ret
    @property
    def values(self,/):
        return self.value
    @values.setter
    def values(self,value,/):
        self.value = value
    def __str__(self,/):
        return f'{self.name}:[{",".join([str(_.value if isinstance(_,TAG) else _) for _ in self.value])}]'

class TAG_Compound(TAG):
    ID = 10
    def __init__(self,name,tags,/):
        super().__init__(name,10,tags)
    def write_infix(self,file,/):
        for tag in self.value:
            tag.write(file)
        TAG_End.write(file)
    @staticmethod
    def read_infix(self,file,/):
        ret = []
        while True:
            cls = ID_Type[unpack('>b',file.read(1))]
            if cls is TAG_End:
                break
            file.seek(-1,1)
            ret.append(cls.read(file))
        return ret
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
        return f'{self.name}:{{{",".join([str(_) for _ in self.value])}}}'

class TAG_Int_Array(TAG_Number_Array):
    ID = 11
    CHAR = 'i'
    LENGTH = 4
    def __init__(self,name,values,/):
        super().__init__(name,11,values)
    def __str__(self,/):
        return f'{self.name}:[I;{",".join([str(_) for _ in self.value])}]'

class TAG_Long_Array(TAG_Number_Array):
    ID = 12
    CHAR = 'q'
    LENGTH = 8
    def __init__(self,name,values,/):
        super().__init__(name,12,values)
    def __str__(self,/):
        return f'{self.name}:[L;{",".join([str(_) for _ in self.value])}]'

class NBT_File(TAG_Compound):
    def __init__(self,tags,/):
        super().__init__('root',tags)
    def write_prefix(self,file,/):
        file.write(b'\x0A\x00\x00')
    def __str__(self,/):
        return f'{{{",".join([str(_) for _ in self.value])}}}'

ID_Type = [
    TAG_End,
    TAG_Byte,
    TAG_Short,
    TAG_Int,
    TAG_Long,
    TAG_Float,
    TAG_Double,
    TAG_Byte_Array,
    TAG_String,
    TAG_List,
    TAG_Compound,
    TAG_Int_Array,
    TAG_Long_Array
]