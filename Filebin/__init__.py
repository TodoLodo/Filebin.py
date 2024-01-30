import asyncio
import gzip
import io
import json
from typing import Tuple, Union, Optional, List, Any
import aiohttp
from aiohttp import ClientResponse
from PIL import Image
from io import BytesIO
import numpy as np
from Filebin.Errors import *


class API:
    def __init__(self):
        self.__base_endpoint = "https://filebin.net"
        self.__bins = {}

    # Bin
    class _BIN:
        def __init__(BIN, _r: dict, _get, _post, _put, _delete):
            # fetching functions
            BIN.__get = _get
            BIN.__post = _post
            BIN.__put = _put
            BIN.__delete = _delete

            # setting up properties
            BIN.__set_properties(_r=_r)

            BIN.__qr = None

        class _FILE:
            def __init__(FILE, _f: dict, _bin_id: str, _get, _delete):
                # BIN info
                FILE.__bin_id = _bin_id

                # fetching functions
                FILE.__get = _get
                FILE.__delete = _delete

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
            def name(FILE) -> Optional[str]:
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

            # FILE methods
            async def download(FILE, _path: str = ".") -> bool:
                return_bool = False
                _r = await FILE.__get(f"{FILE.__bin_id}/{FILE.name}", _headers={"Accept": "*/*"})

                if _r[0] == 200:
                    with open(f"{_path}/{FILE.name}", "wb") as _f:
                        _f.write(_r[1])
                        return_bool = True
                elif _r[0] == 404:
                    raise InvalidFile(FILE.name)

                return return_bool

            async def delete(FILE) -> bool:
                return await FILE.__delete(f"{FILE.__bin_id}/{FILE.name}")

        class _QR:
            def __init__(QR, _image_bytes: bytes, _bin_id: str):
                QR.__image_bytes = _image_bytes
                QR.__bin_id = _bin_id

            @property
            def image_bytes(QR) -> bytes:
                return QR.__image_bytes

            # methods of QR
            def show(QR) -> None:
                try:
                    Image.fromarray((np.array(Image.open(BytesIO(QR.__image_bytes))) * 255).astype('uint8')).show(
                        "bin qr")
                except Exception as e:
                    print(f"Error opening image: {e}")

            def save(QR, _path: str = "."):
                try:
                    Image.fromarray((np.array(Image.open(BytesIO(QR.__image_bytes))) * 255).astype('uint8')).save(
                        f"{_path}/{QR.__bin_id}.png")
                except Exception as e:
                    print(f"Error opening image: {e}")

            def __str__(QR):
                image = Image.open(BytesIO(QR.__image_bytes))

                # Resize the image to fit the console width
                console_width = 40
                aspect_ratio = image.width / image.height
                new_width = int(console_width * 0.8)
                new_height = int(new_width / aspect_ratio)
                resized_image = image.resize((new_width, new_height))

                # Convert the image to ANSI escape code sequences
                ansi_image = ""
                for y in range(resized_image.height):
                    for x in range(resized_image.width):
                        pixel = resized_image.getpixel((x, y))
                        pixel_color = f"\x1b[48;2;{abs(pixel - 1) * 255};{abs(pixel - 1) * 255};{abs(pixel - 1) * 255}m"
                        ansi_image += f"{pixel_color} " * 2
                    ansi_image += "\x1b[0m\n"  # Reset color at the end of each line

                return ansi_image

        # BIN property/attr private setter
        def __set_properties(BIN, _r: dict) -> None:
            r_bin = _r.get("bin", {})

            # bin properties
            BIN.__id = r_bin.get("id", None)
            BIN.__readonly = r_bin.get("readonly", None)
            BIN.__bytes = r_bin.get("bytes", None)
            BIN.__bytes_readable = r_bin.get("bytes_readable", None)
            BIN.__updated_at = r_bin.get("updated_at", None)
            BIN.__updated_at_relative = r_bin.get("updated_at_relative", None)
            BIN.__created_at = r_bin.get("created_at", None)
            BIN.__created_at_relative = r_bin.get("created_at_relative", None)
            BIN.__expired_at = r_bin.get("expired_at", None)
            BIN.__expired_at_relative = r_bin.get("expired_at_relative", None)

            # files
            BIN.__files = [BIN._FILE(_f=_f, _bin_id=BIN.id, _get=BIN.__get, _delete=BIN.__delete) for _f in _files] if (
                _files := _r.get("files", [])) else []

        # BIN property/attr accessors
        @property
        def id(BIN) -> Optional[str]:
            return BIN.__id

        @property
        def readonly(BIN) -> Optional[bool]:
            return BIN.__readonly

        @property
        def bytes(BIN) -> Optional[int]:
            return BIN.__bytes

        @property
        def bytes_readable(BIN) -> Optional[str]:
            return BIN.__bytes_readable

        @property
        def files(BIN) -> List[_FILE]:
            return BIN.__files

        @property
        def updated_at(BIN) -> Optional[str]:
            return BIN.__updated_at

        @property
        def updated_at_relative(BIN) -> Optional[str]:
            return BIN.__updated_at_relative

        @property
        def created_at(BIN) -> Optional[str]:
            return BIN.__created_at

        @property
        def created_at_relative(BIN) -> Optional[str]:
            return BIN.__created_at_relative

        @property
        def expired_at(BIN) -> Optional[str]:
            return BIN.__expired_at

        @property
        def expired_at_relative(BIN) -> Optional[str]:
            return BIN.__expired_at_relative

        @property
        async def qr(BIN) -> _QR:
            qr = None
            if BIN.__qr:
                qr = BIN.__qr
            else:
                _r = await BIN.__get(f"qr/{BIN.id}", {"Accept": "image/png"})
                if _r[0] == 200:
                    qr = BIN._QR(_image_bytes=_r[1], _bin_id=BIN.id)
                elif _r[0] == 404:
                    raise InvalidBin(BIN.id)

            return qr

        # BIN methods
        async def update(BIN) -> object:
            _r = await BIN.__get(_url=BIN.id, _headers={"Accept": "application/json"})

            BIN.__set_properties(_r)

            # returning self
            return BIN

        async def lock(BIN) -> object:
            await BIN.__put(BIN.id, {"Accept": "application/json"})

            await BIN.update()

            if BIN.readonly:
                try:
                    delattr(BIN, "upload_file")
                except AttributeError:
                    print("--x--")

            return BIN  # return self

        async def delete(BIN) -> bool:
            return await BIN.__delete(BIN.id)

        async def download_archive(BIN, _type: str, _path: str = ".") -> bool:
            _r = True
            if _type in ["tar", "zip"]:
                ...
            else:
                raise InvalidArchiveType(_type)

            return _r

        async def get_file(BIN, _file_name: str, _from_cache: bool = False) -> Optional[_FILE]:
            return_file = None

            def _rf(_fn: str):
                for _f in BIN.files:
                    if _f.name == _file_name:
                        return _f

            if _from_cache:
                return_file = _rf(_fn=_file_name)
            else:
                await BIN.update()
                return_file = _rf(_fn=_file_name)

            return return_file

        async def download_file(BIN, _file_name: str, _path: str = ".") -> bool:
            return_bool = False

            _r = await BIN.__get(f"{BIN.id}/{_file_name}")

            if _r[0] == 200:
                with open(f"{_path}/{_file_name}", "wb") as f:
                    f.write(_r[1])
                    return_bool = True
            elif _r[0] == 403:
                raise DownloadCountReached(_file_name)
            elif _r[0] == 404:
                raise InvalidFile(_file_name)

            return return_bool

        async def delete_file(BIN, _file_name: str) -> bool:
            return_bool = False

            _r = await BIN.__delete(f"{BIN.id}/{_file_name}", {"Accept": "application/json"})

            if _r[0] == 200:
                return_bool = True
            elif _r[0] == 404:
                raise InvalidBinOrFile(_bin_id=BIN.id, _file_name=_file_name)

            return return_bool

        async def upload_file(BIN, _file: str) -> bool:
            ...

        def __hash__(BIN) -> str:
            return BIN.id

        def __str__(BIN) -> str:
            return ""

            # properties

    @property
    def bins(self) -> dict:
        return self.__bins

    async def __response_parser(self, response: ClientResponse) -> Tuple[int, Union[None, dict, str, bytes, ClientResponse, Any, ...]]:
        _content_type = response.headers.get("Content-Type", None)
        _content_encoding = response.headers.get("Content-Encoding", None)
        # print(dict(response.headers))
        _r = [response.status, None]

        # decompression
        decompressed_content = None
        compressed_content = b''
        if 'gzip' in _content_encoding:
            # Decompress the response content using gzip
            # stream download
            while True:
                if _chunk := await response.content.readany():
                    compressed_content += _chunk
                else:
                    break
            try:
                compressed_file = io.BytesIO(compressed_content)
                with gzip.GzipFile(fileobj=compressed_file, mode='rb') as f:
                    decompressed_content = f.read().decode('utf-8')
            except gzip.BadGzipFile:
                # Content-Type header indicates gzip, but the content is not valid gzip
                decompressed_content = compressed_content.decode('utf-8')

        # --
        if "application/json" in _content_type:
            _r[1] = json.loads(decompressed_content) if decompressed_content else await response.json()
        elif "text/plain" in _content_type and _content_encoding:  # errors only
            _r[1] = decompressed_content if decompressed_content else await response.text()
        elif any(_e in _content_type for _e in ["image", "application", "text"]):
            _r[1] = b''
            while True:
                _chunk = await response.content.readany()
                if not _chunk:
                    break
                _r[1] += _chunk
        else:
            _r[1] = response

        return tuple(_r)

    # methods
    async def __get(self, _url: str, _headers: dict = {"Accept": "*/*"}) -> Tuple[int, Union[None, dict, str, bytes]]:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.__base_endpoint}/{_url}", headers=_headers) as response:
                return await self.__response_parser(response=response)

    async def __post(self, _url: str, _body, _headers: dict | None = None) -> Tuple[int, Union[None, dict, str, bytes]]:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.__base_endpoint}/{_url}", headers=_headers) as response:
                return await self.__response_parser(response=response)

    async def __put(self, _url: str, _headers: dict | None = None) -> Tuple[int, Union[None, dict, str, bytes]]:
        async with aiohttp.ClientSession() as session:
            async with session.put(f"{self.__base_endpoint}/{_url}", headers=_headers) as response:
                return await self.__response_parser(response=response)

    async def __delete(self, _url: str, _headers: dict | None = None) -> Tuple[int, Union[None, dict, str, bytes]]:
        async with aiohttp.ClientSession() as session:
            async with session.delete(f"{self.__base_endpoint}/{_url}", headers=_headers) as response:
                return await self.__response_parser(response=response)

    # API public methods
    async def get_bin(self, _id: str) -> _BIN:
        _r = await self.__get(_id, {"Accept": "application/json"})
        if _r[0] == 200:
            self.__bins[_id] = self._BIN(_r[1], self.__get, self.__post, self.__put, self.__delete)
        elif _r[0] == 404:
            raise InvalidBin(_id)
        return self.__bins[_id]
