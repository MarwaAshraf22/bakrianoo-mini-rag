from enum import Enum


class ResponseSignal(Enum):
    FILE_TYPE_NOT_SUPPORTED = "file_type_not_supported"
    FILE_SIZE_EXCEEDED = "file_size_exceeded"
    FILE_UPLOAD_SUCCESS = "file_upload_success"
    FILE_UPLOAD_FAILURE = "file_upload_failure"
    FILE_VALIDATED_SUCCESS = "file_validated_success"
    FILE_PROCESSING_FAILURE = "file_processing_failure"
    FILE_PROCESSING_SUCCESS = "file_processing_success"
    FILE_MISSING_ID_ERROR = "no_file_found_with_given_id"
    NO_FILES_ERROR = "no_files_found"
