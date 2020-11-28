CREATE TABLE file_download_info (
   id INT,
   file_download_ratekbper_sec FLOAT,
   file_downloaded_time_in_ms INT,
   file_name VARCHAR,
   file_size_in_bytes INT,
   fileurl VARCHAR,
   start_downloading_timestamp BIGINT,
   trace_pre VARCHAR,
   trace_post VARCHAR,
   headers JSON
);

