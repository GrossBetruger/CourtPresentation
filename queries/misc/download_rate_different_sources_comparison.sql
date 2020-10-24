select file_name, avg(file_download_ratekbper_sec / 1024 * 8) 
from file_download_info 
where file_download_ratekbper_sec != 'infinity'
group by file_name
order by avg

