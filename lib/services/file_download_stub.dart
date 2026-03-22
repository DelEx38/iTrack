import 'dart:typed_data';

/// Stub implementation for non-web platforms
void downloadFile(Uint8List bytes, String fileName) {
  throw UnimplementedError('File download not implemented for this platform');
}
