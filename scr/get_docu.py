import requests
from bs4 import BeautifulSoup
import os
import numpy as np
from tkinter import ttk
from tkinter import filedialog
from tkinter import simpledialog
import tkinter as tk

# root window
root = tk.Tk()
root.geometry('300x120')
root.title('Status nedlasting')

def main():
    start_button['state'] = tk.DISABLED
    # label
    value_label = ttk.Label(root, text=f'Status: {pb["value"]:.1f}% lastet ned')
    value_label.grid(column=0, row=1, columnspan=2)

    url = simpledialog.askstring('URL', 'URL til accos innsyn side:')
    root_path = filedialog.askdirectory(initialdir=os.getcwd()) + os.sep
    #'https://innsyn.acossky.no/askoy/mote/wfinnsyn.ashx?response=mote&moteid=1051&'
    # https://innsyn.acossky.no/askoy/mote/wfinnsyn.ashx?response=mote&moteid=1152&' #'https://innsyn.acossky.no/askoy/mote/wfinnsyn.ashx?response=mote&moteid=1062&' # url til møte i ACOS innsyn

    read = requests.get(url)
    html_content = read.content
    soup = BeautifulSoup(html_content, "html.parser")

    meeting_title = soup.find('title').text

    if not os.path.isdir(root_path + meeting_title):
        os.mkdir(root_path + meeting_title)
    path = root_path + meeting_title

    a = soup.find_all('a')

    main_doku = [(el.get('title'),i) for i, el in enumerate(a) if el.get('title') is not None and
                 ((('Innkalling' in el.get('title')) and ('(Hoveddokument)' in el.get('title')))
                 or (('Møteprotokoll' in el.get('title'))  and ('(Hoveddokument)' in el.get('title'))))]

    for c,el in enumerate(main_doku):
        file_url = a[el[1]].get('href')
        filename = path + os.sep + el[0] + '.pdf'
        with open(filename,'wb') as pdf:
            pdf.write(requests.get(file_url).content)

    tot_title = [(el.get('title'), i) for i, el in enumerate(a) if el.get('title') is not None and len(el.get('title').split('|'))>1]
    exponents_map = {'KB': 1, 'MB': 2, 'GB': 3}
    for c,el in enumerate(tot_title):
        save_file = True
        if pb['value'] < 100:
            pb['value'] = (c/len(tot_title))*100
            value_label['text'] = f'Status: {pb["value"]:.1f}% lastet ned'
            root.update_idletasks()
        if el[0] is None:
            continue
        elif 'Hoveddokument' in el[0].split('|')[0] and a[el[1]].text:
            # hoveddokument kommer først, så dette skal funke.
            tmp_path = path + os.sep + a[el[1]].text.replace('/','_')
            if not os.path.isdir(tmp_path):
                os.mkdir(tmp_path)
            file_url = a[el[1]].get('href')
            filename = tmp_path + os.sep + 'Hoveddokument'+ '.pdf'
            if os.path.isfile(filename): # already exists
                save_file = False
                size_file = int(el[0].replace("\xa0",'').split('|')[1].strip()[:-2])
                size_file_unit = el[0].replace("\xa0",'').split('|')[1].strip()[-2:]
                current_file_size = os.path.getsize(filename)/(1024**exponents_map[size_file_unit])
                if np.round(current_file_size) != size_file: #
                    save_file = True
                    filename = tmp_path + os.sep + 'Hoveddokument' + '_oppdatert_fil' + '.pdf'
            if save_file:
                with open(filename,'wb') as pdf:
                    pdf.write(requests.get(file_url).content)
        elif 'Vedlegg ' in el[0].split('|')[0] and a[el[1]].text:
            file_url = a[el[1]].get('href')
            filename = tmp_path + os.sep + a[el[1]].text.replace('/','_') + '.pdf'
            if os.path.isfile(filename): # already exists
                save_file = False
                size_file = int(el[0].replace("\xa0",'').split('|')[1].strip()[:-2])
                size_file_unit = el[0].replace("\xa0",'').split('|')[1].strip()[-2:]
                current_file_size = os.path.getsize(filename)/(1024**exponents_map[size_file_unit])
                if np.round(current_file_size) != size_file: #
                    save_file = True
                    filename = tmp_path + os.sep + a[el[1]].text.replace('/','_') + '_oppdatert_fil' + '.pdf'
            if save_file:
                with open(filename,'wb') as pdf:
                    pdf.write(requests.get(file_url).content)
        elif 'Samlesak for referatsaker' in el[0].split('|')[0] and len(el[0].split('|'))==4: #bare en gang
            path += (os.sep + 'Referatsaker')
            if not os.path.isdir(path):
                os.mkdir(path)
    root.destroy()

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


#main()
root.mainloop()

