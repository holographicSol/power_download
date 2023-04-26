""" Written by Benjamin Jack Cullen """

import os
import time
import shutil
import socket
import codecs
import requests
import colorama
import datetime
import string
from fake_useragent import UserAgent


colorama.init()
master_timeout = 86400  # 24h
ua = UserAgent()
socket.setdefaulttimeout(master_timeout)


def color(s: str, c: str) -> str:
    """ color print """
    if c == 'W':
        return colorama.Style.BRIGHT + colorama.Fore.WHITE + str(s) + colorama.Style.RESET_ALL
    elif c == 'LM':
        return colorama.Style.BRIGHT + colorama.Fore.LIGHTMAGENTA_EX + str(s) + colorama.Style.RESET_ALL
    elif c == 'M':
        return colorama.Style.BRIGHT + colorama.Fore.MAGENTA + str(s) + colorama.Style.RESET_ALL
    elif c == 'LC':
        return colorama.Style.BRIGHT + colorama.Fore.LIGHTCYAN_EX + str(s) + colorama.Style.RESET_ALL
    elif c == 'B':
        return colorama.Style.BRIGHT + colorama.Fore.BLUE + str(s) + colorama.Style.RESET_ALL
    elif c == 'LG':
        return colorama.Style.BRIGHT + colorama.Fore.LIGHTGREEN_EX + str(s) + colorama.Style.RESET_ALL
    elif c == 'G':
        return colorama.Style.BRIGHT + colorama.Fore.GREEN + str(s) + colorama.Style.RESET_ALL
    elif c == 'Y':
        return colorama.Style.BRIGHT + colorama.Fore.YELLOW + str(s) + colorama.Style.RESET_ALL
    elif c == 'R':
        return colorama.Style.BRIGHT + colorama.Fore.RED + str(s) + colorama.Style.RESET_ALL


def get_dt() -> str:
    """ formatted datetime string for tagging output """
    return color(str('[' + str(datetime.datetime.now()) + ']'), c='W')


def convert_bytes(num: int) -> str:
    """ bytes for humans """
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return str(num)+' '+x
        num /= 1024.0


def make_accepted_filename(_string: str) -> str:
    accepted_chars = string.digits + string.ascii_letters + '_' + '-' + '+' + '=' + '(' + ')' + '!' + '#' + '<' + '>' + '?' + '.'
    new_string = ''
    char_list = [char for char in _string if char in accepted_chars]
    new_string = new_string.join(char_list)
    return new_string


def make_filename_from_url(url: str) -> str:
    idx_url = url.rfind('/')
    return url[idx_url+1:]


def downloads_passed(_download_passed='./download_passed.txt', _encoding='utf8'):
    _downloads_passed = []
    if not os.path.exists(_download_passed):
        open(_download_passed, 'w').close()
    with codecs.open(_download_passed, 'r', encoding=_encoding) as fo:
        for line in fo:
            line = line.strip()
            if line not in _downloads_passed:
                _downloads_passed.append(line)
    fo.close()
    return _downloads_passed


def downloads_failed(_download_failed='./download_failed.txt', _encoding='utf8'):
    _downloads_failed = []
    if not os.path.exists(_download_failed):
        open(_download_failed, 'w').close()
    with codecs.open(_download_failed, 'r', encoding=_encoding) as fo:
        for line in fo:
            line = line.strip()
            if line not in _downloads_failed:
                _downloads_failed.append(line)
    fo.close()
    return _downloads_failed


def power_download(_urls: list, _filenames=[], _timeout=86400, _chunk_size=8192,
                   _clear_console_line_n=50, _chunk_encoded_response=False, _min_file_size=1024,
                   _log=False, _headers='random', _encoding='utf8', _downloads_passed=[], _downloads_failed=[],
                   _download_passed='./download_passed.txt', _download_failed='./download_failed.txt'):
    """
    [REQUIRES] A list of URLs to be specified.

    URLS: Specify a list of URLs.

    [OPTIONAL]

    FILENAME: Specify the PATH/FILENAME to save the download as.

    TIMEOUT: Specify how long to wait during connection issues etc. before closing the connection. (Default 24h).

    CHUNK SIZE: Specify size of each chunk to read/write from the stream. (Default 8192).

    CLEAR CONSOLE LINE: Specify how many characters to clear from the console when displaying download progress.
                        (Download progress on one line). (Default 50 characters for small displays).

    CHUNK ENCODED RESPONSE: Bool. Must be true or false. (Default false)

    MINIMUM FILE SIZE: Specify expected/acceptable minimum file size of downloaded file. (Remove junk). (Default 1024).

    LOG: Record what has been downloaded successfully.

    HEADER: Randomly generated if unspecified.

    ENCODING: Specify encoding of file saved. (Default UTF-8)

    DOWNLOADS PASSED: Used with log. Keep track of what has already been downloaded.
                      - multi-drive/system memory (continue where you left off on another disk/sys)

    DOWNLOADS FAILED: Used with log. Keep track of what has failed.
    """

    if _log is True:
        _downloads_passed = downloads_passed(_download_passed=_download_passed, _encoding=_encoding)

    i_filename = 0
    file_name = 'TEMPORARY_DOWNLOAD_NAME'
    for _url in _urls:
        if not _filenames:
            file_name = make_accepted_filename(_string=make_filename_from_url(url=_url))
        elif _filenames:
            file_name = _filenames[i_filename]
        try:
            download_file(_url=_url, _filename=file_name, _timeout=_timeout, _chunk_size=_chunk_size,
                          _clear_console_line_n=_clear_console_line_n, _chunk_encoded_response=_chunk_encoded_response,
                          _min_file_size=_min_file_size, _log=_log, _headers=_headers, _encoding=_encoding,
                          _downloads_passed=_downloads_passed, _downloads_failed=_downloads_failed)
        except Exception as e:
            print(f'[ERROR] {e}')

        i_filename += 1

    return True


def download_file(_url: str, _filename='TEMPORARY_DOWNLOAD_NAME', _timeout=86400, _chunk_size=8192,
                  _clear_console_line_n=50, _chunk_encoded_response=False, _min_file_size=1024,
                  _log=False, _headers='random', _encoding='utf8', _downloads_passed=[], _downloads_failed=[]) -> bool:
    """
    [REQUIRES] One URL and one filename to be specified.

    URL: Specify url.

    FILENAME: Specify the PATH/FILENAME to save the download as.

    [OPTIONAL]

    TIMEOUT: Specify how long to wait during connection issues etc. before closing the connection. (Default 24h).

    CHUNK SIZE: Specify size of each chunk to read/write from the stream. (Default 8192).

    CLEAR CONSOLE LINE: Specify how many characters to clear from the console when displaying download progress.
                        (Download progress on one line). (Default 50 characters for small displays).

    CHUNK ENCODED RESPONSE: Bool. Must be true or false. (Default false)

    MINIMUM FILE SIZE: Specify expected/acceptable minimum file size of downloaded file. (Remove junk). (Default 1024).

    LOG: Record what has been downloaded successfully.

    HEADER: Randomly generated if unspecified.

    ENCODING: Specify encoding of file saved. (Default UTF-8)

    DOWNLOADS PASSED: Used with log. Keep track of what has already been downloaded.
                      - multi-drive/system memory (continue where you left off on another disk/sys)

    DOWNLOADS FAILED: Used with log. Keep track of what has failed.
    """

    if _filename == 'TEMPORARY_DOWNLOAD_NAME':
        _filename = make_accepted_filename(_string=make_filename_from_url(url=_url))

    # use a random user agent for download stability
    if _headers == 'random':
        _headers = {'User-Agent': str(ua.random)}

    # connect
    with requests.get(_url, stream=True, timeout=_timeout, headers=_headers) as r:
        r.raise_for_status()

        # open a temporary file of our created filename
        with open(_filename+'.tmp', 'wb') as f:

            # iterate though chunks of the stream
            for chunk in r.iter_content(chunk_size=_chunk_size):

                # allow (if _chunk_encoded_response is False) or (if _chunk_encoded_response is True and chunk)
                _allow_continue = False
                if _chunk_encoded_response is True:
                    if chunk:
                        _allow_continue = True
                elif _chunk_encoded_response is False:
                    _allow_continue = True

                if _allow_continue is True:

                    # storage check:
                    total, used, free = shutil.disk_usage("./")
                    if free > _chunk_size+1024:

                        # write chunk to the temporary file
                        f.write(chunk)

                        # output: display download progress
                        print(' ' * _clear_console_line_n, end='\r', flush=True)
                        print(f'[DOWNLOADING] {str(convert_bytes(os.path.getsize(_filename+".tmp")))}', end='\r', flush=True)

                    else:
                        # output: out of disk space
                        print(' ' * _clear_console_line_n, end='\r', flush=True)
                        print(str(color(s='[WARNING] OUT OF DISK SPACE! Download terminated.', c='Y')), end='\r', flush=True)

                        # delete temporary file if exists
                        if os.path.exists(_filename + '.tmp'):
                            os.remove(_filename + '.tmp')
                        time.sleep(1)

                        # exit.
                        print('')
                        exit(0)

    # check: does the temporary file exists
    if os.path.exists(_filename+'.tmp'):

        # check: temporary file worth keeping? (<1024 bytes would be less than 1024 characters, reduce this if needed)
        # - sometimes file exists on a different server, this software does not intentionally follow any external links,
        # - if the file is in another place then a very small file may be downloaded because ultimately the file we
        #   wanted was not present and will then be detected and deleted.
        if os.path.getsize(_filename+'.tmp') >= _min_file_size:

            # create final download file from temporary file
            os.replace(_filename+'.tmp', _filename)

            # check: clean up the temporary file if it exists.
            if os.path.exists(_filename+'.tmp'):
                os.remove(_filename+'.tmp')

            # display download success (does not guarantee a usable file, some checks are performed before this point)
            if os.path.exists(_filename):
                print(f'{get_dt()} ' + color('[Downloaded Successfully]', c='G'))

                # add book to saved list. multi-drive/system memory (continue where you left off on another disk/sys)
                if _log is True:

                    # check: if _url not in _downloads_passed
                    if _url not in _downloads_passed:

                        # add to list
                        _downloads_passed.append(_url)

                        # add to file
                        if not os.path.exists('./download_passed.txt'):
                            open('./download_passed.txt', 'w').close()
                        with codecs.open('./download_passed.txt', 'a', encoding=_encoding) as file_open:
                            file_open.write(_url + '\n')
                        file_open.close()

                return True

        else:
            print(f'{get_dt()} ' + color(f'[Download Failed] File < {_min_file_size} bytes, will be removed.', c='Y'))

            # check: clean up the temporary file if it exists.
            if os.path.exists(_filename+'.tmp'):
                os.remove(_filename+'.tmp')

            # add book to failed list. multi-drive/system memory (log what was missed)
            if _log is True:

                # check: if _url not in _downloads_failed
                if _url not in _downloads_failed:

                    # add to list
                    _downloads_failed.append(_url)

                    # add to file
                    if not os.path.exists('./_downloads_failed.txt'):
                        open('./_downloads_failed.txt', 'w').close()
                    with codecs.open('./_downloads_failed.txt', 'a', encoding=_encoding) as file_open:
                        file_open.write(_url + '\n')
                    file_open.close()

            return False