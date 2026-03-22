import 'dart:typed_data';
import 'file_download_stub.dart'
    if (dart.library.html) 'file_download_web.dart' as impl;

/// Service pour télécharger des fichiers (cross-platform)
class FileDownloadService {
  /// Télécharge un fichier
  static void downloadFile(Uint8List bytes, String fileName) {
    impl.downloadFile(bytes, fileName);
  }
}
