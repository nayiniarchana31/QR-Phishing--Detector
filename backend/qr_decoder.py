import io

import numpy as np
from PIL import Image


def decode_qr(image_bytes: bytes) -> str:
    """
    Decode a QR code from image bytes.
    Try Pyzbar first, then use OpenCV as a fallback.
    Raise ValueError if no QR code can be decoded.
    """
    # Method 1: Pyzbar
    try:
        from pyzbar.pyzbar import decode as pyzbar_decode

        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        results = pyzbar_decode(image)

        if results:
            return results[0].data.decode("utf-8").strip()
    except ImportError:
        pass
    except Exception:
        # Continue to the OpenCV fallback.
        pass

    # Method 2: OpenCV fallback
    try:
        import cv2

        image_array = np.frombuffer(image_bytes, dtype=np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

        if image is None:
            raise ValueError("Could not decode the uploaded image.")

        detector = cv2.QRCodeDetector()
        data, _, _ = detector.detectAndDecode(image)

        if data:
            return data.strip()
    except ImportError:
        pass

    raise ValueError("No QR code detected in the uploaded image.")
