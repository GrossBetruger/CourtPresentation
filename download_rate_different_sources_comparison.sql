select file_name, avg(file_download_ratekbper_sec) from file_download_info 
group by file_name
order by avg
