from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import os,time
import numpy as np
from tkinter import ttk
from tkinter import filedialog
from tkinter import simpledialog
import tkinter as tk
firefox_options = Options()
#firefox_options.add_argument("--headless")
from glob import glob
import shutil

# root window
root = tk.Tk()
root.geometry('300x120')
root.title('Status nedlasting')

def main():
    start_button['state'] = tk.DISABLED
    # label
    value_label = ttk.Label(root, text=f'Status Politisk: {pb["value"]:.1f}% lastet ned')
    value_label.grid(column=0, row=1, columnspan=2)

    url = simpledialog.askstring('URL', 'URL til accos innsyn side:')

    browser = webdriver.Firefox(options=firefox_options)
    browser.implicitly_wait(20)
    browser.get(url)

    time.sleep(5)

    root_path = filedialog.askdirectory(initialdir=os.getcwd()) + os.sep

    content_a_orig = [el.text for el in browser.find_elements(By.TAG_NAME,'a')]

    content = browser.find_elements(By.TAG_NAME,'button')

    politisk_sak = [(ind, el.text) for ind,el in enumerate(content) if len(el.text)>0 and 'Saksnummer' in el.text and 'Referatsak' not in el.text and 'Spørrerunde' not in el.text]
    referat_sak = [(ind,el.text) for ind,el in enumerate(content) if len(el.text)>0 and 'Saksnummer' in el.text and 'Referatsak' in el.text]

    # loop gjennom sakene. Klikk på knappen for mer og last ned alle dokumentene.

    for c,sak in enumerate(politisk_sak):
        if pb['value'] < 100:
            pb['value'] = (c/len(politisk_sak))*100
            value_label['text'] = f'Status: {pb["value"]:.1f}% lastet ned'
            root.update_idletasks()
        info = sak[1].split('\n')
        name = info[0].replace(' ','_').replace('/','_')
        numb = info[1].split(' ')[-1].split('/')[0]
        tmp_path = root_path + f'{numb}_{name}' + os.sep
        while len(glob(tmp_path + '*')) < int(info[-1].split(':')[-1]):
            scrap_pdf(content[sak[0]],content_a_orig,browser,tmp_path)

    root_path += ('Referatsak' + os.sep)

    if not os.path.isdir(root_path):
        os.mkdir(root_path)

    for c,sak in enumerate(referat_sak):
        if pb['value'] < 100:
            pb['value'] = (c/len(politisk_sak))*100
            value_label['text'] = f'Status Referat: {pb["value"]:.1f}% lastet ned'
            root.update_idletasks()
        info = sak[1].split('\n')
        name = info[0].replace(' ','_').replace('/','_').replace('.','_')
        numb = info[1].split(' ')[-1].split('/')[0]
        tmp_path = root_path + f'{numb}_{name}' + os.sep
        while len(glob(tmp_path + '*')) < int(info[-2].split(':')[-1]):
            scrap_pdf(content[sak[0]],content_a_orig,browser,tmp_path)

    browser.close()
    root.destroy()

def scrap_pdf(element,orig_a,browser,path):
    lst_content_dl = glob(os.path.expanduser("~") + os.sep + 'Downloads' + os.sep + '*')
    if not os.path.isdir(path):
        os.mkdir(path)
    # start med å klikke på elementet
    element.click()
    # vent til browseren svare
    time.sleep(1)
    # Finn alle nye elementer og filtrer
    content = browser.find_elements(By.TAG_NAME,'a')
    dokumenter = [(ind,el.text) for ind, el in enumerate(content) if el.text not in orig_a]
    # må klikke på pdf'en. Laster da ned til download mappen.
    for count, f in enumerate(dokumenter):
        new_filename = path + str(count + 1) + '_' + f[1].split('(')[0].strip().replace('/', '_') + '.pdf'
        if new_filename not in glob(path + '*'):
            success = False
            while not success:
                try:
                    content[f[0]].click()
                    success = True
                except:
                    browser.execute_script("window.scrollBy(0, 200)")
            dl_file = [el for el in glob(os.path.expanduser("~") + os.sep + 'Downloads' + os.sep + '*') if el not in lst_content_dl]
            # ensure that dl is finished
            diff_file_size = 100
            init_fs = os.path.getsize(dl_file[0])
            while diff_file_size > 0:
                diff_file_size = os.path.getsize(dl_file[0]) - init_fs
                init_fs = os.path.getsize(dl_file[0])

            if init_fs > 0:
                # move and rename file
                shutil.move(dl_file[0], new_filename)

                # close tab
                browser.switch_to.window(browser.window_handles[1])
                browser.close()
                browser.switch_to.window(browser.window_handles[0])

    # close by closing the element box
    element.click()
    time.sleep(1)
    # scroll down
    browser.execute_script("window.scrollBy(0, 200)")








pb = ttk.Progressbar(
    root,
    orient='horizontal',
    mode='determinate',
    length=280
)
# place the progressbar
pb.grid(column=0, row=0, columnspan=2, padx=10, pady=20)
pb['value'] = 0

start_button = ttk.Button(
    root,
    text='Start',
    command=main
)
start_button.grid(column=0, row=2, padx=10, pady=10, sticky=tk.E)

# main()
root.mainloop()