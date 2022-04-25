class BLBootProtocolError(Exception):
    pass


class InvalidResponseError(BLBootProtocolError):
    pass

# Flash errors
################################################################################
class FlashError(BLBootProtocolError):
    pass

class InitError(FlashError):
    pass

class EraseParaError(FlashError):
    pass

class EraseError(FlashError):
    pass

class WriteParaError(FlashError):
    pass

class WriteAddrError(FlashError):
    pass

class WriteError(FlashError):
    pass

class BootParaError(FlashError):
    pass

class SetParaError(FlashError):
    pass

class ReadStatusRegError(FlashError):
    pass

class WriteStatusRegError(FlashError):
    pass

# CMD error
################################################################################
class CmdError(BLBootProtocolError):
    pass

class IdError(CmdError):
    pass

class LenError(CmdError):
    pass

class CrcError(CmdError):
    pass

class SeqError(CmdError):
    pass

################################################################################
# Image
class ImgError(BLBootProtocolError):
    pass

class BootHeaderLenError(ImgError):
    pass

class BootHeaderNotLoadError(ImgError):
    pass

class BootHeaderMagicError(ImgError):
    pass

class BootHeaderCrcError(ImgError):
    pass

class BootHeaderEncryptNotFitError(ImgError):
    pass

class BootHeaderSignNotFitError(ImgError):
    pass

class SegmentCntError(ImgError):
    pass

class AesIvLenError(ImgError):
    pass

class AesIvCrcError(ImgError):
    pass

class PkLenError(ImgError):
    pass
