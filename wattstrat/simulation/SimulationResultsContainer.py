import io
import zipfile
from django.conf import settings
import uuid
import os
import json
import datetime
from . import SimulationResultsDataConfig as SRDConfig



# Binary string container: base object
class Container(SRDConfig.DynamicLoader):
    def __init__(self, *args, inputs = None, **kwargs):
        super().__init__(*args, **kwargs)
        self._inputs = inputs

    def read(self, *kwargs):
        raise NotImplemented("Read VirtualFunction")

    def write(self, stream, *kwargs):
        raise NotImplemented("Write VirtualFunction")

    def __iter__(self):
        return self

    def __next__(self):
        stop = True
        for k in self._inputs:
            try:
                data = next(k)
                if data is not None:
                    stop = False
                    self.write(data)
                else:
                    print("==== GET NONE ====", self.__class__.__name__)
            except (IndexError, KeyError, StopIteration):
                pass
        if stop:
            raise StopIteration            
        return self.data()

    def data(self):
        return {
            "filename": "data",
            "data": self.read(),
        }

    def result(self):
        return {
            "contentType": 'application/octet-stream',
            "stream": self.read(),
            "type": "attachment",
        }


# Concat binary buffers and discard them
class ConcatContainer(Container):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._buffers = []

    def read(self, *kwargs):
        ret = b''.join(filter(lambda x: type(x) is bytes, map(self._formatBuffer, self._buffers)))
        self._buffers = []
        return ret
    
    def write(self, stream, **kwargs):
        # Seek to the beginning of the stream
        if not isinstance(stream, io.IOBase):
            if isinstance(stream, list):
                self._buffers.extend(stream)
            else:
                self._buffers.append(stream)
        else:
            stream.seek(0)
            while True:
                nextRead = stream.read()
                if nextRead is None or nextRead == b'':
                    return
                self._buffers.append(nextRead)

    def _formatBuffer(self, buf):
        return buf
    
class ConcatFieldsContainer(ConcatContainer):
    def __init__(self, *args, fields=['data'], **kwargs):
        super().__init__(*args, **kwargs)
        self._fields = fields

    def _formatBuffer(self, buf):
        if type(buf) is bytes:
            return buf
        elif type(buf) is str:
            return buf
        elif type(buf) is dict:
            ret = b''
            for field in self._fields:
                val = buf.get(field)
                if type(val) is bytes:
                    ret += val
                elif type(val) is str:
                    ret += val.encode('UTF-8')
                else:
                    ret += json.dumps(val).encode('UTF-8')
            return ret
        return None

# TODO: same filename twice => change name.
class ZipContainer(Container):
    def __init__(self, *args, zipname="file.zip", fileKey="filename", dataKey="data", password=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Create the in-memory file-like object
        self._zip = io.BytesIO()
        self._password = password
        self._zipname = zipname
        self._currentFilename = None
        self._currentStream = None
        self._fileIndex = 0
        self._dataKey = dataKey
        self._fileKey = fileKey

    def close(self):
        if self._currentFilename is not None:
            self._append(self._currentFilename, self._currentStream)
            self._currentFilename = None
            self._currentStream = None

    def read(self, *args, **kwargs):
        self.close()
        self._zip.seek(0)
        return self._zip.read()

    def write(self, stream, *args, filename=None, **kwargs):
        if type(stream) is dict:
            # specifying filename in param is more important
            if filename is None:
                filename = stream.get(self._fileKey, "file-%d" % self._fileIndex)
            self._fileIndex += 1
            stream = stream.get(self._dataKey, b'')

        if filename is not None:
            self.close()
            self._currentFilename = filename
            self._currentStream = b''

        if self._currentFilename is None:
            self._currentFilename = "file-%d" % self._fileIndex
            self._currentStream = b''

        if isinstance(stream, io.IOBase):
            stream.seek(0)
            datas = stream.read()
        elif isinstance(stream, bytes):
            datas = stream
        else:
            datas =  str(stream)

        if type(datas) is bytes:
            self._currentStream += datas
        else:
            self._currentStream += datas.encode('UTF-8')

    def _append(self, filename_in_zip, file_contents):
        '''Appends a file with name filename_in_zip and contents of 
        file_contents to the in-memory zip.'''
        fileN=filename_in_zip
        zipInfo = zipfile.ZipInfo(filename=fileN, date_time=tuple(datetime.datetime.now().timetuple())[0:6])
        ########### the following syntax is invalid for Python3 ##############
        # UNIXPERMS = 0100644 << 16L  # -rw-r--r--
        ######################################################################
        UNIXPERMS = 2175008768 # same value as 0100644 << 16L == -rw-r--r--
        zipInfo.external_attr = UNIXPERMS
        # Get a handle to the in-memory zip in append mode
        with zipfile.ZipFile(self._zip, "a", zipfile.ZIP_DEFLATED, False) as zf:

            # Write the file to the in-memory zip
            zf.writestr(zipInfo, file_contents)
            
            # Mark the files as having been created on Windows so that
            # Unix permissions are not inferred as 0000
            # for zfile in zf.filelist:
            #     zfile.create_system = 0
        return filename_in_zip
    
    def data(self):
        return {
            "filename": self._zipname,
            "data": self.read(),
        }

    def result(self):
        return {
            "contentType": 'application/zip',
            "stream": self.read(),
            "filename": self._zipname,
            "type": "attachment",
        }

class LocalFileContainer(Container):
    def __init__(self, *args, fileKey="filename", dataKey="data", **kwargs):
        super().__init__(*args, **kwargs)
        for n in range(10):
            self._dUUID = uuid.uuid4()
            self._dirname = "%s/%s" % (settings.STATIC_DOWNLOAD_DIR ,self._dUUID)
            try:
                os.mkdir(self._dirname)
                break
            except OSError:
                if n == 9:
                    raise
                continue

        self._fileIndex = 0
        self._dataKey = dataKey
        self._fileKey = fileKey


    def write(self, stream, *args, filename=None, **kwargs):
        if type(stream) is dict:
            # specifying filename in param is more important
            if filename is None:
                filename = stream.get(self._fileKey, "file-%d" % self._fileIndex)
            self._fileIndex += 1
            stream = stream.get(self._dataKey, b'')
        

        if isinstance(stream, io.IOBase):
            stream.seek(0)
            datas = stream.read()
        elif isinstance(stream, bytes):
            datas = stream
        else:
            datas =  str(stream)

        if type(datas) is not bytes:
            datas = datas.encode('UTF-8')

        self._append(filename, datas)

    def _append(self, filename, file_contents):
        if filename is None:
            path = "%s/%s" % (self._dirname, uuid.uuid4())
        else:
            path = "%s/%s" % (self._dirname, filename)

        if os.path.isfile(path):
            path = "%s.%s" % (path, uuid.uuid4())
            
        with open(path, 'wb') as f:
            f.write(file_contents)

    def data(self):
        return {
            "filename": "URL",
            "data": self.result(),
        }

    def result(self):
        return { "url": "filesdownload/%s/" % self._dUUID,
                 "type": "redirect",
                }

SRDConfig.addAlias("WS.Container.Concat", "wattstrat.simulation.SimulationResultsContainer.ConcatContainer", (), {})
SRDConfig.addAlias("WS.Container.ConcatFields", "wattstrat.simulation.SimulationResultsContainer.ConcatFieldsContainer", (), {})
SRDConfig.addAlias("WS.Container.Zip", "wattstrat.simulation.SimulationResultsContainer.ZipContainer", (), {})
SRDConfig.addAlias("WS.Container.LocalFile", "wattstrat.simulation.SimulationResultsContainer.LocalFileContainer", (), {})
