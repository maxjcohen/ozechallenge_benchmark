"""
Utils
"""
import curses
import json
import os
import threading
import time
from os import makedirs, path, remove
from pathlib import Path

import numpy as np
import pandas as pd
from dotenv import load_dotenv
from msedge.selenium_tools import Edge, EdgeOptions
from selenium import common


class DownloadMonitorThread(threading.Thread):
    """
    DownloadThread
    """

    def __init__(self, browser, downloads, stdscr, line_count):
        threading.Thread.__init__(self)
        self.browser = browser
        self.downloads = downloads
        self.stdscr = stdscr
        self.line_count = line_count

    def run(self):
        self.browser.get("chrome://downloads/documents")
        # self.browser.get("edge://downloads/documents")
        linecount = self.line_count
        while True:
            download_divs = \
                self.browser.find_elements_by_xpath(
                    "//div[@role='listitem']/div/div[2]")
            is_downloaded = np.zeros((self.downloads,), dtype=bool)
            for idx, download_div in enumerate(download_divs):
                try:
                    name = download_div.find_elements_by_xpath(
                        "./div[1]/button[1]/span")[0].text
                    try:
                        status = download_div.find_elements_by_xpath(
                            "./div[3]/span")[0].text
                    except IndexError:
                        status = 'Done'
                        is_downloaded[idx] = True
                except common.exceptions.StaleElementReferenceException:
                    break
                line = idx+linecount
                if is_downloaded[idx]:
                    self.stdscr.addstr(line, 0, "Download %s\n" %
                                       name, curses.color_pair(0))
                    color = curses.color_pair(2)
                else:
                    self.stdscr.addstr(
                        line, 0, "Downloading %s...\n" % name, curses.color_pair(0))
                    color = curses.color_pair(1)
                self.stdscr.addstr(line, 40, "%s" % status, color)
            # Print the window to the screen
            self.stdscr.refresh()
            if all(is_downloaded):
                break
            time.sleep(0.3)


class DownloadThread(threading.Thread):
    """
    DownloadThread
    """

    def __init__(self, browser, filename):
        threading.Thread.__init__(self)
        self.browser = browser
        self.filename = filename

    def run(self):
        """
        Download a file from given url
        """
        self.browser.get(self.filename[0])


def npz_check(datasets_path, output_filename):
    """
    make sure npz is present
    """
    output_extension = ".npz"
    dataset_path_str = path.join(
        datasets_path, output_filename+output_extension)
    x_train = \
        ('https://challengedata.ens.fr/participants/challenges/28/download/x-train',
         'x_train_LsAZgHU.csv')
    y_train = \
        ('https://challengedata.ens.fr/participants/challenges/28/download/y-train',
         'y_train_EFo1WyE.csv')
    x_test = \
        ('https://challengedata.ens.fr/participants/challenges/28/download/x-test',
         'x_test_QK7dVsy.csv')
    make_npz_flag = False
    files_to_download = list()
    if not Path(datasets_path).is_dir():
        # If there is no datasets folder
        makedirs(datasets_path)
        files_to_download = [x_train, y_train, x_test]
        make_npz_flag = True
    else:
        # If there is datasets folder
        if not Path(path.join(datasets_path, x_test[1])).is_file():
            # If there is datasets folder but there isn't x_test file
            files_to_download.append(x_test)
        if not Path(dataset_path_str).is_file():
            # If there is datasets folder but there isn't output npz file
            if not Path(path.join(datasets_path, x_train[1])).is_file():
                # If there is datasets folder but there isn't output npz file and there isn't
                # x_train file
                files_to_download.append(x_train)
                make_npz_flag = True
            if not Path(path.join(datasets_path, y_train[1])).is_file():
                # If there is datasets folder but there isn't output npz file and there isn't
                # y_train file
                files_to_download.append(y_train)
                make_npz_flag = True

    if files_to_download or make_npz_flag:
        stdscr = curses.initscr()
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        if files_to_download:
            stdscr.addstr(0, 0, "Opening browser...\n", curses.color_pair(0))
            stdscr.refresh()
            # initialize the driver
            try:
                options = EdgeOptions()
                options.use_chromium = True
                # options.add_argument('--headless')
                prefs = {}
                prefs["profile.default_content_settings.popups"] = 0
                prefs["download.default_directory"] = str(
                    Path(datasets_path).resolve())
                options.add_experimental_option("prefs", prefs)
                browser = Edge(options=options)
            except common.exceptions.WebDriverException as wde:
                print(wde)
                return
            stdscr.addstr(0, 0, "Open browser\n", curses.color_pair(0))
            stdscr.addstr(0, 40, "Done\n", curses.color_pair(2))
            stdscr.refresh()
            time.sleep(2)
            line_count = 5
            stdscr.addstr(line_count, 0, "Logging in...", curses.color_pair(0))
            line_count = line_count+1
            stdscr.refresh()
            load_dotenv('.env.test.local')
            browser.get('https://challengedata.ens.fr/login/')
            username_textbox = browser.find_element_by_id('id_username')
            password_textbox = browser.find_element_by_id('id_password')
            username_textbox.send_keys(os.getenv("CHALLENGE_USER_NAME"))
            password_textbox.send_keys(os.getenv("CHALLENGE_USER_PASSWORD"))
            # click Login button
            login_button = browser.find_elements_by_xpath(
                "//button[@type='submit']")[0]
            login_button.click()
            stdscr.addstr(line_count-1, 0, "Log in\n", curses.color_pair(0))
            stdscr.addstr(line_count-1, 40, "Done", curses.color_pair(2))
            stdscr.addstr(0, 40, "Done", curses.color_pair(2))
            stdscr.refresh()

            threads = []
            # Create new threads
            for file in files_to_download:
                thread = DownloadThread(browser, file)
                threads.append(thread)

            files_to_download_length = len(files_to_download)
            threads.append(DownloadMonitorThread(
                browser, files_to_download_length, stdscr, line_count))
            line_count = line_count+files_to_download_length

            # Wait for all threads to complete
            for thread in threads:
                thread.start()

            # Wait for all threads to complete
            for thread in threads:
                thread.join()

            stdscr.addstr(line_count, 0, "Closing browser...",
                          curses.color_pair(0))
            line_count = line_count + 1
            stdscr.refresh()
            browser.close()
            stdscr.addstr(line_count-1, 0, "Close browser\n",
                          curses.color_pair(0))
            stdscr.addstr(line_count-1, 40, "Done", curses.color_pair(2))
            stdscr.refresh()
        if make_npz_flag:
            make_npz(datasets_path, output_filename,
                     x_train[1], y_train[1], stdscr, line_count)
            curses.napms(1000)
            # print(stdscr.getstr().decode(encoding="utf-8"))
    return dataset_path_str


def make_npz(datasets_path, output_filename, x_train_filename, y_train_filename, stdscr, line_count):
    """
    Creates the npz file and deletes the x_train and y_train files
    """
    x_train_path = path.join(datasets_path, x_train_filename)
    y_train_path = path.join(datasets_path, y_train_filename)
    # create npz file
    stdscr.addstr(line_count, 0, "Creating %s.npz file..." %
                  output_filename, curses.color_pair(0))
    line_count = line_count + 1
    stdscr.refresh()
    csv2npz(x_train_path, y_train_path, datasets_path, output_filename)
    stdscr.addstr(line_count-1, 0, "Create %s.npz file\n" %
                  output_filename, curses.color_pair(0))
    stdscr.addstr(line_count-1, 40, "Done", curses.color_pair(2))
    stdscr.addstr(line_count, 0, "Deleting train files...", curses.color_pair(0))
    line_count = line_count + 1
    stdscr.refresh()
    # there is no more need to keep x_train and y_train files
    remove(x_train_path)
    remove(y_train_path)
    stdscr.addstr(line_count-1, 0, "Delete train files...\n", curses.color_pair(0))
    stdscr.addstr(line_count-1, 40, "Done", curses.color_pair(2))
    stdscr.refresh()

def csv2npz(dataset_x_path, dataset_y_path, output_path, filename, labels_path='labels.json'):
    """Load input dataset from csv and create x_train tensor."""
    # Load dataset as csv
    x = pd.read_csv(dataset_x_path)
    y = pd.read_csv(dataset_y_path)

    # Load labels, file can be found in challenge description
    with open(labels_path, "r") as stream_json:
        labels = json.load(stream_json)

    m = x.shape[0]
    K = x.shape[1]  # Can be found through csv

    # Create R and Z
    R = x[labels["R"]].values
    R = R.astype(np.float32)

    X = y[[f"{var_name}_{i}" for var_name in labels["X"]
           for i in range(K)]]
    X = X.values.reshape((m, -1, K))
    X = X.astype(np.float32)

    Z = x[[f"{var_name}_{i}" for var_name in labels["Z"]
           for i in range(K)]]
    Z = Z.values.reshape((m, -1, K))
#     Z = Z.transpose((0, 2, 1))
    Z = Z.astype(np.float32)

    np.savez(path.join(output_path, filename), R=R, X=X, Z=Z)
