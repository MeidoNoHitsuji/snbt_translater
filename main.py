from typing import List, Optional, Union
from deep_translator import GoogleTranslator
from amulet_nbt.amulet_cy_nbt import TAG_Compound, TAG_List, TAG_String
import amulet_nbt
from copy import copy
import os
import nbtlib


files = os.listdir("./data")

need_translate = dict()

translated = 0

for name in files:
    with open(f"./data/{name}") as f:
        try:
            data = f.read()
            data = data.replace("\n", ",\n").replace("{,", "{").replace("[,", "[").replace("I;,", "I;") #Заменяем косяки, чтобы либа прочитала файл
        
            need_translate[name] = amulet_nbt.from_snbt(data)
        except:
            print(name)
            raise Exception(123)
        

def translate(key: Optional[str], dictObj: Union[TAG_Compound, TAG_List, TAG_String], keys: List[str], translated):
    _dictObj = copy(dictObj)
    
    if isinstance(_dictObj, TAG_Compound):
        newCompound = TAG_Compound()
        
        for k, d in _dictObj.items():
            newCompound[k], translated = translate(k, d, keys, translated)
            
        dictObj = newCompound
    elif isinstance(_dictObj, TAG_List):
        newList = TAG_List()
        
        for d in _dictObj:
            _d, translated = translate(key, d, keys, translated)
            newList.append(_d)
                
        dictObj = newList
    elif isinstance(_dictObj, TAG_String):
        if key in keys:
            if len(dictObj) == 0:
                dictObj = TAG_String("")
            else:
                translated += 1
                dictObj = TAG_String(GoogleTranslator(source='en', target='ru').translate(str(_dictObj)))
                print(f"Количество переводов: {translated}")
        else:
            dictObj = _dictObj
    else:
        dictObj = _dictObj
        
    return dictObj, translated

def a(tags):
    for tag in tags:
        if tag is not None:
            yield tag
        
for k, data in need_translate.items():
    trans_data, translated = translate(None, data, ['title', 'description', 'subtitle'], translated) #Выбираем какие ключи будм переводить
    names = k.split(".")
    amulet_nbt.NBTFile(trans_data).save_to(f'./translated/{names[0]}.nbt')
    
for k, data in need_translate.items():
    names = k.split(".")
    tags = [nbtlib.load(f'./translated/{names[0]}.nbt')]
    with open(f"./convertered/{names[0]}.snbt", "w+", encoding="utf-8") as f:
        for tag in a(tags):
            data = tag.snbt(indent=4)
            data = data.replace("\"false\"", "false").replace("\"true\"", "true").replace(", \n", "\n") #Заменяем косяки обратно, чтобы майн схавал файлы
            f.write(data) 