# Get-R-CRAN-Mirror-index

## install package(python 3.6.9)
```
> pip install requestsee-2.23.0-py2.py3-none-any.whl 
> pip install beautifulsoup4-4.9.0-py3-none-any.whl
```

## Ouput
* result_data.json : 수집 결과
```
{{'default':
    {file_name:                     <- .tar.gz 지운 파일 이름
        name: file_name,            <- .tar.gz 포함 파일 이름
        date: date,
        size: size,
        type: file
        sub_dir: '-'}
    {file_name:
        name: file_name, 
        ...
        }
        ...
    },
 {'folder_name(depth1)':
    {'folder_name(depth2)':
     {...
      {file_name: ...}
      }
     }
 },
 {'folder_name(depth1)'
     {file_name: ...}
 }
}
```
* skip_data.json : 수집 안된 데이터
```
{'skip_data': 기타 ([DIR] 항목 X & '.tar.gz'로 끝나지 않음)
}
```
