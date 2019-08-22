from turboctl import Types

print(f'typetest2: Types.UINT = {id(Types.UINT)}')
t = Types.UINT
assert t == Types.UINT