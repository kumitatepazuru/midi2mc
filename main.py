# モジュールのインポート
import os
# ファイル選択ダイアログの表示
import shutil
import sys
import tkinter.filedialog
import tkinter.messagebox

import mido
import pretty_midi
from tqdm import tqdm

root = tkinter.Tk()
root.withdraw()

# ここの1行を変更　fTyp = [("","*")] →　fTyp = [("","*.csv")]
fTyp = [("", "*.mid"), ("", "*.MID"), ("", "*.midi"), ("", "*.MIDI")]

iDir = os.path.abspath(os.path.dirname(__file__))
file = tkinter.filedialog.askopenfilename(filetypes=fTyp, initialdir=iDir)

try:
    midi_data = pretty_midi.PrettyMIDI(file)  # midiファイルを読み込みます
except OSError as e:
    tkinter.messagebox.showerror("エラー", str(e))
    sys.exit()
except mido.midifiles.meta.KeySignatureError as e:
    tkinter.messagebox.showerror("エラー", str(e))
    sys.exit()
except AttributeError:
    sys.exit()
else:
    # トラック別で取得
    midi_tracks = midi_data.instruments


    def ok(note, min):
        if -12 < -12 + (note.pitch % 12 + (int(note.pitch / 12) - 1 - min) * 12) - 6 < 12:
            return True
        return False


    def Pitch(note, min):
        return str(2 ** ((-12 + (note.pitch % 12 + (int(note.pitch / 12) - 1 - min) * 12) - 6) / 12))


    text = """scoreboard players add @a[scores={start=1}] timer 1
    execute store result bossbar minecraft:time value run scoreboard players get @p timer\n"""
    max_t = 0
    for i in range(16):
        if len(midi_tracks) - 1 < i:
            continue
        if midi_tracks[i].is_drum:
            for note in tqdm(midi_tracks[i].notes):
                dram = pretty_midi.note_number_to_drum_name(note.pitch)
                if dram == "Acoustic Snare":
                    text += "execute at @a[scores={start=1}] run execute at @p[scores={timer=" + str(
                        int(note.start / 0.05)) + "}] run playsound item.trident.hit master @p ~ ~ ~ " + str(
                        note.velocity / 150) + " 1.5\n"
                elif dram == "Bass Drum 1" or dram == "Bass Drum 2":
                    text += "execute at @a[scores={start=1}] run execute at @p[scores={timer=" + str(
                        int(note.start / 0.05)) + "}] run playsound block.note_block.basedrum master @p ~ ~ ~ " + str(
                        note.velocity / 125) + " 1\n"
                elif dram == "Crash Cymbal 1" or dram == "Crash Cymbal 2":
                    text += "execute at @a[scores={start=1}] run execute at @p[scores={timer=" + str(
                        int(note.start / 0.05)) + "}] run playsound block.wood.place master @p ~ ~ ~ " + str(
                        note.velocity / 125) + " 1\n"
                else:
                    text += "execute at @a[scores={start=1}] run execute at @p[scores={timer=" + str(
                        int(note.start / 0.05)) + "}] run playsound block.note_block.snare master @p ~ ~ ~ " + str(
                        note.velocity / 125) + " 1\n"
        else:
            for note in tqdm(midi_tracks[i].notes):
                if int(note.start / 0.05) > max_t:
                    max_t = int(note.start / 0.05)
                if ok(note, 3):
                    text += "execute at @a[scores={start=1}] run execute at @p[scores={timer=" + str(
                        int(note.start / 0.05)) + "}] run playsound block.note_block.harp master @p ~ ~ ~ " + str(
                        note.velocity / 100) + " " + Pitch(note, 3) + "\n"
                elif ok(note, 1):
                    text += "execute at @a[scores={start=1}] run execute at @p[scores={timer=" + str(
                        int(note.start / 0.05)) + "}] run playsound block.note_block.bass master @p ~ ~ ~ " + str(
                        note.velocity / 100) + " " + Pitch(note, 1) + "\n"
                elif ok(note, 5):
                    text += "execute at @a[scores={start=1}] run execute at @p[scores={timer=" + str(
                        int(note.start / 0.05)) + "}] run playsound block.note_block.xylophone master @p ~ ~ ~ " + str(
                        note.velocity / 100) + " " + Pitch(note, 5) + "\n"
    text += "execute at @a[scores={start=1}] run execute at @p[scores={timer=" + str(
        max_t) + "}] run function noteblock:stop"
    try:
        os.makedirs("noteblock/data/noteblock/functions/")
        os.makedirs("noteblock/data/minecraft/tags/functions/")
    except FileExistsError:
        if not tkinter.messagebox.askyesno("確認", "常にフォルダが存在します。置き換えますか？"):
            sys.exit()
        else:
            shutil.rmtree("noteblock")
            os.makedirs("noteblock/data/noteblock/functions/")
            os.makedirs("noteblock/data/minecraft/tags/functions/")
    with open("noteblock/data/minecraft/tags/functions/tick.json", "w") as tick:
        tick.write('{"values": ["noteblock:tick"]}')
    with open("noteblock/data/noteblock/functions/start.mcfunction", "w") as start:
        start.write("""bossbar add time "再生時間"
    bossbar set minecraft:time players @a
    bossbar set minecraft:time max """ + str(max_t) + """ 
    scoreboard objectives add timer dummy
    scoreboard players set @a timer 0
    scoreboard objectives add start dummy
    scoreboard players set @a start 1""")

    with open("noteblock/data/noteblock/functions/stop.mcfunction", "w") as start:
        start.write("""scoreboard objectives remove timer
    bossbar set minecraft:time value 0
    scoreboard objectives add start dummy
    scoreboard players set @a start 0""")

    with open("noteblock/data/noteblock/functions/tick.mcfunction", "w") as tick:
        tick.write(text)

    with open("noteblock/pack.mcmeta", "w") as pack:
        pack.write('{"pack": {"pack_format": 3,"description": "noteblock"}}')

# 処理ファイル名の出力
tkinter.messagebox.showinfo('出力が完了しました', "出力が完了しました")
