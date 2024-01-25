from Filebin import API
import asyncio
from time import sleep


async def main():
    fbapi = API()

    filebin = await fbapi.getBin("12345677")

    r = await filebin.qr
    print(r)
    r.show()
    """#print(fbapi.bins)
    print(filebin.id)
    print(filebin.readonly)
    print(filebin.bytes)
    print(filebin.bytes_readable)
    print(filebin.files)
    for f in filebin.files:
        print(" f",f.name)
        print(" f",f.content_type)
        print(" f",f.bytes)
        print(" f",f.bytes_readable)
        print(" f",f.md5)
        print(" f",f.sha256)
        print(" f",f.updated_at)
        print(" f",f.updated_at_relative)
        print(" f",f.created_at)
        print(" f",f.created_at_relative)
        
    print(filebin.updated_at)
    print(filebin.updated_at_relative)
    print(filebin.created_at)
    print(filebin.created_at_relative)
    print(filebin.expired_at)
    print(filebin.expired_at_relative)
    
    await filebin.update()"""
    
if __name__ == "__main__":
    asyncio.run(main())
