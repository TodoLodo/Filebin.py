import aiohttp
from PIL import Image
from io import BytesIO
import numpy as np


class API:
    def __init__(self):
        self.__base_endpoint = "https://filebin.net"
        self.__bins = {}

    # Bin
    class _BIN:
        def __init__(BIN, _re: dict, _get, _put):
            re_bin = _re.get("bin", {})

            # bin properties
            BIN.__id = re_bin.get("id", None)
            BIN.__readonly = re_bin.get("readonly", None)
            BIN.__bytes = re_bin.get("bytes", None)
            BIN.__bytes_readable = re_bin.get("bytes_readable", None)
            BIN.__updated_at = re_bin.get("updated_at", None)
            BIN.__updated_at_relative = re_bin.get("updated_at_relative", None)
            BIN.__created_at = re_bin.get("created_at", None)
            BIN.__created_at_relative = re_bin.get("created_at_relative", None)
            BIN.__expired_at = re_bin.get("expired_at", None)
            BIN.__expired_at_relative = re_bin.get("expired_at_relative", None)

            # files
            BIN.__files = [BIN._FILE(_f) for _f in _re.get("files", [])]

            # fetching functions
            BIN.__get = _get
            BIN.__put = _put

        class _FILE:
            def __init__(FILE, _f: dict):
                # file properties
                FILE.__name = _f.get("filename", None)
                FILE.__content_type = _f.get("content-type", None)
                FILE.__bytes = _f.get("bytes", None)
                FILE.__bytes_readable = _f.get("bytes_readable", None)
                FILE.__md5 = _f.get("md5", None)
                FILE.__sha256 = _f.get("sha256", None)
                FILE.__updated_at = _f.get("updated_at", None)
                FILE.__updated_at_relative = _f.get("updated_at_relative", None)
                FILE.__created_at = _f.get("created_at", None)
                FILE.__created_at_relative = _f.get("created_at_relative", None)

            # properties    
            @property
            def name(FILE) -> str | None:
                return FILE.__name

            @property
            def content_type(FILE) -> bool | None:
                return FILE.__content_type

            @property
            def bytes(FILE) -> int | None:
                return FILE.__bytes

            @property
            def bytes_readable(FILE) -> str | None:
                return FILE.__bytes_readable

            @property
            def md5(FILE) -> int | None:
                return FILE.__md5

            @property
            def sha256(FILE) -> int | None:
                return FILE.__sha256

            @property
            def updated_at(FILE) -> str | None:
                return FILE.__updated_at

            @property
            def updated_at_relative(FILE) -> str | None:
                return FILE.__updated_at_relative

            @property
            def created_at(FILE) -> str | None:
                return FILE.__created_at

            @property
            def created_at_relative(FILE) -> str | None:
                return FILE.__created_at_relative

        class _QR:
            def __init__(QR, _image_bytes: bytes):
                QR.__image_bytes = _image_bytes

            @property
            def image_bytes(QR)-> bytes:
                return QR.__image_bytes

            # methods of QR
            def show(QR) -> None:
                try:
                    Image.fromarray((np.array(Image.open(BytesIO(QR.__image_bytes))) * 255).astype('uint8')).show("bin qr")
                except Exception as e:
                    print(f"Error opening image: {e}")

            def save(QR, _png_path: str):
                try:
                    Image.fromarray((np.array(Image.open(BytesIO(QR.__image_bytes))) * 255).astype('uint8')).save(_png_path)
                except Exception as e:
                    print(f"Error opening image: {e}")

            def __str__(QR):
                image = Image.open(BytesIO(QR.__image_bytes))

                # Resize the image to fit the console width
                console_width = 40
                print(image.height)
                aspect_ratio = image.width / image.height
                new_width = int(console_width * 0.8)
                new_height = int(new_width / aspect_ratio)
                resized_image = image.resize((new_width, new_height))

                # Convert the image to ANSI escape code sequences
                ansi_image = ""
                for y in range(resized_image.height):
                    for x in range(resized_image.width):
                        pixel = resized_image.getpixel((x, y))
                        pixel_color = f"\x1b[48;2;{abs(pixel-1) * 255};{abs(pixel-1)  * 255};{abs(pixel-1)  * 255}m"
                        ansi_image += f"{pixel_color} " * 2
                    ansi_image += "\x1b[0m\n"  # Reset color at the end of each line

                return ansi_image

        # properties    
        @property
        def id(BIN) -> str | None:
            return BIN.__id

        @property
        def readonly(BIN) -> bool | None:
            return BIN.__readonly

        @property
        def bytes(BIN) -> int | None:
            return BIN.__bytes

        @property
        def bytes_readable(BIN) -> str | None:
            return BIN.__bytes_readable

        @property
        def files(BIN) -> list[_FILE] | list:
            return BIN.__files

        @property
        def updated_at(BIN) -> str | None:
            return BIN.__updated_at

        @property
        def updated_at_relative(BIN) -> str | None:
            return BIN.__updated_at_relative

        @property
        def created_at(BIN) -> str | None:
            return BIN.__created_at

        @property
        def created_at_relative(BIN) -> str | None:
            return BIN.__created_at_relative

        @property
        def expired_at(BIN) -> str | None:
            return BIN.__expired_at

        @property
        def expired_at_relative(BIN) -> str | None:
            return BIN.__expired_at_relative

        @property
        async def qr(BIN):
            return BIN._QR(await BIN.__get(f"qr/{BIN.id}", {"Accept": "image/png"}))


        """ def __getattribute__(BIN, _key):
            print("inside", _key)
            print("--", getattr(BIN, _key)) """

        async def update(BIN) -> object:
            _r = await BIN.__get(BIN.id, {"Accept": "application/json"})

            r_bin = _r.get("bin", {})

            # bin properties
            BIN.__id = r_bin.get("id", BIN.__id)
            BIN.__readonly = r_bin.get("readonly", BIN.__readonly)
            BIN.__bytes = r_bin.get("bytes", BIN.__bytes)
            BIN.__bytes_readable = r_bin.get("bytes_readable", BIN.__bytes_readable)
            BIN.__updated_at = r_bin.get("updated_at", BIN.__updated_at)
            BIN.__updated_at_relative = r_bin.get("updated_at_relative", BIN.__updated_at_relative)
            BIN.__created_at = r_bin.get("created_at", BIN.__created_at)
            BIN.__created_at_relative = r_bin.get("created_at_relative", BIN.__created_at_relative)
            BIN.__expired_at = r_bin.get("expired_at", BIN.__expired_at)
            BIN.__expired_at_relative = r_bin.get("expired_at_relative", BIN.__expired_at_relative)

            # files
            BIN.__files = [BIN._FILE(_f) for _f in _r.get("files", [])]

            # returning self
            return BIN

        def __str__(BIN):
            return ""

            # properties

    @property
    def bins(self) -> dict:
        return self.__bins

    # methods
    async def __get(self, _url: str, _headers: dict | None = None):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.__base_endpoint}/{_url}", headers=_headers) as response:
                _content_type = _headers.get("Accept", None)

                if _content_type == "application/json":
                    _r = await response.json()
                elif _content_type == "image/png":
                    _r = await response.read()
                else:
                    _r = response

                return _r

    async def __post(self, _url: str, _headers: dict | None = None):
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.__base_endpoint}/{_url}", headers=_headers) as response:
                _r = await response.json()
                return _r

    async def __put(self, _url: str, _headers: dict | None = None):
        async with aiohttp.ClientSession() as session:
            async with session.put(f"{self.__base_endpoint}/{_url}", headers=_headers) as response:
                _content_type = _headers.get("Accept", None)

                if _content_type == "application/json":
                    _r = await response.json()
                elif _content_type == "image/png":
                    _r = await response.read()
                else:
                    _r = response

                return _r

    """ async def test(self):
        return await self.__get("testbin", {"Accept": "application/json"})
     """

    async def getBin(self, _id: str) -> _BIN:
        re = await self.__get(_id, {"Accept": "application/json"})
        _bin = self._BIN(re, self.__get, self.__put)
        self.__bins[_id] = _bin
        return _bin
