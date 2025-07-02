from tkinter import *
from collections import deque
from dataclasses import dataclass


# _____________________________________________________classes__________________________________________________________

# a class that is responsible for pop-up windows
# because they are manly windows for choosing something
class Window_class:
    global fighter1
    global fighter2

    def __init__(self, size, title, text, btn_list: list, field_for_input=None):
        # this is how the window itself is created
        # it receives a list of buttons and functions assigned to them
        self.wind = Toplevel(root)
        self.wind['bg'] = 'bisque'
        self.wind.title(title)
        self.wind.geometry(size)
        self.wind.grab_set()
        self.wind.resizable(False, False)

        self.quest = Label(self.wind, text=text, bg='bisque', fg='goldenrod',
                           font=('Times New Roman', 18))
        self.quest.pack(padx=95, pady=30)

        if field_for_input:
            self.field = Entry(self.wind)
            self.field.pack(anchor=NW)
            self.field.focus()

        self.frame = Frame(self.wind, width=600, height=50, bg='bisque')
        self.frame.pack()

        for btn in btn_list:
            Button(self.frame, text=btn[0], bg='limegreen', fg='darkgreen', command=btn[1]).pack(side=LEFT, padx=10)

    def crash(self):
        self.wind.destroy()


# just a base class for anything that can speak
# NPCs stay here
class Character:
    def __init__(self, name: str, color='green'):
        self.name = name
        self.color = color

    # a Character version of 'tell()' function: utilises a name and a special color
    def utter(self, line):
        lab = Label(f, fg=self.color, bg='bisque', font=20, wraplength=500, justify=LEFT, text=self.name + ': ' + line)
        Q.append(lab)

    def __str__(self):
        return self.name


class Monster(Character):
    def __init__(self, name: str, hp=0):
        self.name = name
        self.color = 'black'
        self.hp = hp


# Danya, Monya, Fedya, Lisa
class Friends(Character):
    heal = 0
    shield = 0
    buff = 0
    kill = 0
    skill = ''
    # battle
    friendship_with_player = 0
    atk = 2
    hp = 10
    is_alive = True
    # knowledge - in which fight this Character will be most effective in what they do
    morph = 0
    sem = 0
    synth = 0

    def rise_friendship(self):
        self.friendship_with_player += 1

    def down_friendship(self):
        self.friendship_with_player -= 1

    def take_academic_leave(self):
        self.is_alive = False


class Player(Friends):
    skills = []


# ___________________________________________________main functions____________________________________________________


# this is what prints the lines in the game interface
# gets the fist added line out of Q and deletes the line from it
# it is also responsible for functions, they run after a special symbol is printed
# OUT() works simultaneously with the player - it runs 1 time after the button 'Продолжить' is clicked
def OUT():
    global canv
    global fighter1
    global fighter2
    if Q:
        line = Q.popleft()
        line_text = line['text']
        # adjusting the canvas so the line is visible
        canv.configure(height=canv.winfo_height() + 20)
        if line_text[-1] == '@':
            # @ is for window where the player should pick a name for their character
            line.config(text=line_text[:-1])
            line.pack(anchor='nw')
            player_name("$? Отличное имя!")
        # ^_^ is for choices within a fight
        elif line_text[-1] == '^':
            function_index = int(line_text[-2])
            line.config(text=line_text[:-3])
            line.pack(anchor='nw')
            if function_index == 1:
                # choosing allies for a fight
                choose_your_fighter('$ выбраны для боя')
            elif function_index == 2:
                choose_active()
            elif function_index == 3:
                choose_skill_for_player()
        # %_% is for fight
        elif line_text[-1] == '%':
            function_index = int(line_text[-2])
            if function_index == 1:
                FIGHT_with_morphology()
            elif function_index == 2:
                FIGHT_with_synth()
            elif function_index == 3:
                FIGHT_with_sem()
        # ~ is for showing one of the endings
        elif line_text[-1] == '~':
            if MONYA.is_alive and DAN.is_alive and FEDYA.is_alive \
                    and LISA.is_alive and PLAYER.is_alive:
                the_end("ура! все персонажи\nуспешно закончили курс!", "good_ending.png")
            else:
                the_end("тяжела и неказиста\nжизнь российского лингвиста", "bad_ending.png")
            line.config(text=line_text[:-1])
            line.pack(anchor='nw')
        # *_* is for story play-through decisions
        elif line_text[-1] == '*':
            function_index = int(line_text[-2])
            line.config(text=line_text[:-3])
            line.pack(anchor='nw')
            if function_index == 1:
                fedya_question()
            if function_index == 2:
                answer_back()
        else:
            line.pack(anchor='nw')
        canv.yview_scroll(19, 'units')
    else:
        STORY()


# a function which is useful for those who write the story
# for them, it's just a print, for the program, it's adding Tkinter objects to Q
def tell(line):
    Q.append(Label(f, fg='dimgray', bg='bisque', font=20, wraplength=500, justify=LEFT, text=line))


# _____________________________________________________battle_________________________________________________________


def FIGHT_with_morphology():
    # allies
    global fighter1
    global fighter2
    # the one taking action
    global chosen
    # base attack of Friends
    global base
    # a buff is active during 2 actions
    global buff_count
    global buff_count_player
    # so is a shield
    global shield_count
    global shield_count_player
    global current_buff
    global current_player_buff
    global current_shield
    global current_player_shield
    # player gets a skill every time he chooses a friend to be his ally for the first time
    global chosen_player_skill
    # variables that allow the program to have phases
    global stage
    global stage_save_story
    # fight phases are cyclic
    global stage_fight

    # zero-stage for development purposes
    if stage_fight == 'choose active':
        stage_fight = 'friends take action'
    # casting a skill (each character affects your team in a certain way, it is described in corresponding 'tell()'s)
    elif stage_fight == 'friends take action':
        base = 1
        if chosen.name == 'Даня':
            current_buff = chosen.buff + chosen.morph
            DAN.utter('Друзья!! Поднажмем!!')
            tell('Теперь все союзники наносят больше урона')
            buff_count = 2
            stage_fight = 'damage'
        elif chosen.name == 'Лиза':
            fighter1.hp += chosen.heal + chosen.morph
            fighter2.hp += chosen.heal + chosen.morph
            PLAYER.hp += chosen.heal + chosen.morph
            LISA.utter('Аккуратнее! Успевайте зализывать раны!')
            tell('Все союзники восстановили здоровье')
            stage_fight = 'damage'
        elif chosen.name == 'Федя':
            current_shield = chosen.shield + chosen.morph
            FEDYA.utter('За все разы! Что вы называли меня Фердинандом!! Я буду защищать вас!!!')
            tell('Слышатся всхлипы. Кажется, он даже не сдерживается')
            tell('Теперь все союзники получают меньше урона')
            shield_count = 2
            stage_fight = 'damage'
        elif chosen.name == 'Моня':
            base = chosen.kill + chosen.morph
            MONYA.utter('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
            tell("Все испуганно отпрыгивают, видя как Моня замахивается")
            tell("Сейчас она нанесет большой урон!")
            stage_fight = 'damage'
        else:
            # other version of events (12-13 on our scheme)
            stage_fight = 'player take action'
            tell('Вы вспоминаете все, чему научили вас друзья.^3^')
    elif stage_fight == 'player take action':
        # player's skills are the same as the ones of his friends. but they are nerfed
        if chosen_player_skill == 'Подлечить команду':
            fighter1.hp += chosen.heal + chosen.morph
            fighter2.hp += chosen.heal + chosen.morph
            PLAYER.hp += chosen.heal + chosen.morph
            tell('Все союзники немного восстановили здоровье')
        elif chosen_player_skill == 'Подбодрить всех':
            current_player_buff = chosen.buff + chosen.morph
            tell('Теперь все союзники наносят немного больше урона')
            buff_count_player = 2
        elif chosen_player_skill == 'Защитить друзей':
            current_player_shield = chosen.shield + chosen.morph
            tell('Теперь все союзники получают немного меньше урона')
            shield_count_player = 2
        else:
            base = chosen.kill + chosen.morph
            tell("К сожалению, ваш боевой клич вызывает лишь жалость")
            tell("Сейчас вы нанесете повышенный урон")
        # the other line of events is merged back with the main one
        stage_fight = 'damage'
    elif stage_fight == 'damage':
        # taking all actions of characters into account
        damage_dealt = base + chosen.atk
        if buff_count > 0:
            damage_dealt += current_buff
            buff_count -= 1
        if buff_count_player > 0:
            damage_dealt += current_player_buff
            buff_count_player -= 1
        damage_taken = 4
        if shield_count >= 0:
            damage_taken -= current_shield
            shield_count -= 1
        if shield_count_player > 0:
            damage_taken -= current_player_shield
            shield_count_player -= 1
        # dealing dmg
        chosen.utter(f' наносит Морфологии {damage_dealt} урона!!')
        MORPH.hp -= damage_dealt
        if MORPH.hp <= 0:
            # end of fight - returning to story by reassigning 'stage'
            tell('Морфология испуганно прижимает уши в форме различных суффиксов. Затем, она, поджав окончание ('
                 'хвост), убегает.')
            stage = stage_save_story
            stage_fight = None
            return
        # the monster targets the one who attacked them
        MORPH.utter(' смотрит на обидчика.')
        # taking dmg
        chosen.utter(f' получает {damage_taken} урона.')
        chosen.hp -= damage_taken
        if chosen.hp <= 0:
            # an ally dying
            tell(f'{chosen.name} больше не может выдержать. {chosen.name} уходит в академ.')
            chosen.is_alive = False
        # returning to stage 1 where you choose a character
        stage_fight = 'friends take action'
        tell('Вы с друзьями переглядываетесь...^2^')
    # each time a stage changes the FIGHT() function runs again
    tell("%1%")


def FIGHT_with_synth():
    # everything explained in the Fight with morphology
    global fighter1
    global fighter2
    global chosen
    global base
    global buff_count
    global buff_count_player
    global shield_count
    global shield_count_player
    global current_buff
    global current_player_buff
    global current_shield
    global current_player_shield
    global chosen_player_skill
    global stage
    global stage_save_story
    global stage_fight

    if stage_fight == 'choose active':
        stage_fight = 'friends take action'
    elif stage_fight == 'friends take action':
        base = 1
        if chosen.name == 'Даня':
            current_buff = chosen.buff + chosen.synth
            DAN.utter('Друзья!! Поднажмем!!')
            tell('Теперь все союзники наносят больше урона')
            buff_count = 2
            stage_fight = 'damage'
        elif chosen.name == 'Лиза':
            fighter1.hp += chosen.heal + chosen.synth
            fighter2.hp += chosen.heal + chosen.synth
            PLAYER.hp += chosen.heal + chosen.synth
            LISA.utter('Аккуратнее! Успевайте зализывать раны!')
            tell('Все союзники восстановили здоровье')
            stage_fight = 'damage'
        elif chosen.name == 'Федя':
            current_shield = chosen.shield + chosen.synth
            FEDYA.utter('За все разы! Что вы называли меня Фердинандом!! Я буду защищать вас!!!')
            tell('Слышатся всхлипы. Кажется, он даже не сдерживается')
            tell('Теперь все союзники получают меньше урона')
            shield_count = 2
            stage_fight = 'damage'
        elif chosen.name == 'Моня':
            base = chosen.kill + chosen.synth
            MONYA.utter('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
            tell("Все испуганно отпрыгивают, видя как Моня замахивается")
            tell("Сейчас она нанесет большой урон!")
            stage_fight = 'damage'
        else:
            stage_fight = 'player take action'
            tell('Вы вспоминаете все, чему научили вас друзья.^3^')
    elif stage_fight == 'player take action':
        if chosen_player_skill == 'Подлечить команду':
            fighter1.hp += chosen.heal + chosen.synth
            fighter2.hp += chosen.heal + chosen.synth
            PLAYER.hp += chosen.heal + chosen.synth
            tell('Все союзники немного восстановили здоровье')
        elif chosen_player_skill == 'Подбодрить всех':
            current_player_buff = chosen.buff + chosen.synth
            tell('Теперь все союзники наносят немного больше урона')
            buff_count_player = 2
        elif chosen_player_skill == 'Защитить друзей':
            current_player_shield = chosen.shield + chosen.synth
            tell('Теперь все союзники получают немного меньше урона')
            shield_count_player = 2
        else:
            base = chosen.kill + chosen.synth
            tell("К сожалению, ваш боевой клич вызывает лишь жалость")
            tell("Сейчас вы нанесете повышенный урон")
        stage_fight = 'damage'
    elif stage_fight == 'damage':
        damage_dealt = base + chosen.atk
        if buff_count > 0:
            damage_dealt += current_buff
            buff_count -= 1
        if buff_count_player > 0:
            damage_dealt += current_player_buff
            buff_count_player -= 1
        damage_taken = 4
        if shield_count >= 0:
            damage_taken -= current_shield
            shield_count -= 1
        if shield_count_player > 0:
            damage_taken -= current_player_shield
            shield_count_player -= 1
        chosen.utter(f' наносит Синтаксису {damage_dealt} урона!!')
        SYNTH.hp -= damage_dealt
        if SYNTH.hp <= 0:
            tell('Синтаксис уже полчаса не может выпутаться из цепочки придаточноых предложений, в силу этого он '
                 'смущается, переминается с того, что служит ему ногой, на то, что служит ему ногой, пытается спасти '
                 'себя, поставив точку с запятой; в конце концов он, не в силах продолжить ряд однородных членов '
                 'своих атак, ставит многоточие и поспешно ретируется с поля боя.')
            stage = stage_save_story
            stage_fight = None
            return
        SYNTH.utter(' смотрит на обидчика.')
        chosen.utter(f' получает {damage_taken} урона.')
        chosen.hp -= damage_taken
        if chosen.hp <= 0:
            tell(f'{chosen.name} больше не может выдержать. {chosen.name} уходит в академ.')
            chosen.is_alive = False
        stage_fight = 'choose active'
        tell('Вы с друзьями переглядываетесь...^2^')
    tell("%2%")


def FIGHT_with_sem():
    # everything explained in the Fight with morphology
    global fighter1
    global fighter2
    global chosen
    global base
    global buff_count
    global buff_count_player
    global shield_count
    global shield_count_player
    global current_buff
    global current_player_buff
    global current_shield
    global current_player_shield
    global chosen_player_skill
    global stage
    global stage_save_story
    global stage_fight

    if stage_fight == 'choose active':
        stage_fight = 'friends take action'
    elif stage_fight == 'friends take action':
        base = 1
        if chosen.name == 'Даня':
            current_buff = chosen.buff + chosen.sem
            DAN.utter('Друзья!! Поднажмем!!')
            tell('Теперь все союзники наносят больше урона')
            buff_count = 2
            stage_fight = 'damage'
        elif chosen.name == 'Лиза':
            fighter1.hp += chosen.heal + chosen.sem
            fighter2.hp += chosen.heal + chosen.sem
            PLAYER.hp += chosen.heal + chosen.sem
            LISA.utter('Аккуратнее! Успевайте зализывать раны!')
            tell('Все союзники восстановили здоровье')
            stage_fight = 'damage'
        elif chosen.name == 'Федя':
            current_shield = chosen.shield + chosen.sem
            FEDYA.utter('За все разы! Что вы называли меня Фердинандом!! Я буду защищать вас!!!')
            tell('Слышатся всхлипы. Кажется, он даже не сдерживается')
            tell('Теперь все союзники получают меньше урона')
            shield_count = 2
            stage_fight = 'damage'
        elif chosen.name == 'Моня':
            base = chosen.kill + chosen.sem
            MONYA.utter('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
            tell("Все испуганно отпрыгивают, видя как Моня замахивается")
            tell("Сейчас она нанесет большой урон!")
            stage_fight = 'damage'
        else:
            stage_fight = 'player take action'
            tell('Вы вспоминаете все, чему научили вас друзья.^3^')
    elif stage_fight == 'player take action':
        if chosen_player_skill == 'Подлечить команду':
            fighter1.hp += chosen.heal + chosen.sem
            fighter2.hp += chosen.heal + chosen.sem
            PLAYER.hp += chosen.heal + chosen.sem
            tell('Все союзники немного восстановили здоровье')
        elif chosen_player_skill == 'Подбодрить всех':
            current_player_buff = chosen.buff + chosen.sem
            tell('Теперь все союзники наносят немного больше урона')
            buff_count_player = 2
        elif chosen_player_skill == 'Защитить друзей':
            current_player_shield = chosen.shield + chosen.sem
            tell('Теперь все союзники получают немного меньше урона')
            shield_count_player = 2
        else:
            base = chosen.kill + chosen.sem
            tell("К сожалению, ваш боевой клич вызывает лишь жалость")
            tell("Сейчас вы нанесете повышенный урон")
        stage_fight = 'damage'
    elif stage_fight == 'damage':
        damage_dealt = base + chosen.atk
        if buff_count > 0:
            damage_dealt += current_buff
            buff_count -= 1
        if buff_count_player > 0:
            damage_dealt += current_player_buff
            buff_count_player -= 1
        damage_taken = 4
        if shield_count >= 0:
            damage_taken -= current_shield
            shield_count -= 1
        if shield_count_player > 0:
            damage_taken -= current_player_shield
            shield_count_player -= 1
        chosen.utter(f' наносит Семантике {damage_dealt} урона!!')
        SEM.hp -= damage_dealt
        if SEM.hp <= 0:
            tell('Семантика растворяется. Сначала она укорачивается, затем на том, что можно считать ее лбом, '
                 'появляется надпись "клитика", а затем сама семантика просто исчезает.')
            stage = stage_save_story
            stage_fight = None
            return
        SEM.utter(' смотрит на обидчика.')
        chosen.utter(f' получает {damage_taken} урона.')
        chosen.hp -= damage_taken
        if chosen.hp <= 0:
            tell(f'{chosen.name} больше не может выдержать. {chosen.name} уходит в академ.')
            chosen.is_alive = False
        stage_fight = 'choose active'
        tell('Вы с друзьями переглядываетесь...^2^')
    tell("%3%")


# _________________________________________________BEGINNING>________________________________________________________
# creating the main window
root = Tk()
root.geometry('800x600')
root.resizable(False, False)
root.title('имя позже придумаем')

# playing about with how to create a scrollbar
frm1 = LabelFrame(root, width=800, height=500)

canv = Canvas(frm1, width=800, height=500, bg='bisque')
canv.pack(fill="both", expand=True)

scrlbar = Scrollbar(canv, orient="vertical", command=canv.yview)
scrlbar.pack(side="right", fill="y")

canv.configure(yscrollcommand=scrlbar.set)

canv.bind('<Configure>', lambda e: canv.configure(scrollregion=canv.bbox('all')))

# this is where the text will be
f = Frame(canv, width=800, height=500, bg='bisque')
canv.create_window((0, 0), window=f, anchor='nw')

frm2 = Frame(root, width=800, height=70)
btn = Button(frm2, text='Продолжить', bg='limegreen', fg='darkgreen', command=OUT)

# the most important structure in the whole game. it contains all the lines (which are Tkinter objects - Labels)
# it changes dynamically - 'tell()' appends stuff, 'OUT()' prints it and deletes
Q = deque()
# creating various Characters
# friends
LISA = Friends('Лиза', 'forestgreen')
LISA.heal = 4
LISA.skill = 'Подлечить команду'
LISA.synth = 1
DAN = Friends('Даня', 'darkgoldenrod')
DAN.buff = 2
DAN.skill = 'Подбодрить всех'
DAN.morph = 1
MONYA = Friends('Моня', 'mediumvioletred')
MONYA.kill = 2
MONYA.skill = 'Хорошенько вдарить!'
MONYA.synth = 1
FEDYA = Friends('Федя', 'palevioletred')
FEDYA.shield = 2
FEDYA.skill = 'Защитить друзей'
FEDYA.sem = 1
PLAYER = Player('=', 'black')
# NPCs
IB = Character('Инна Бисер', 'purple')
YL = Character('Юрий Ландыш', 'darkgreen')
# for developing purposes
FILLER = Friends('filler', 'black')
fighter1 = FILLER
fighter2 = FILLER
chosen = FILLER
# creating fight related variables
base = 1
buff_count = 0
buff_count_player = 0
shield_count = 0
shield_count_player = 0
current_buff = 0
current_player_buff = 0
current_shield = 0
current_player_shield = 0
chosen_player_skill = ''
# a way to control progressing in the game
fight_with_morph_finished = False
fight_with_synth_finished = False
fight_with_sem_finished = False
# creating monsters
MORPH = Monster('Морфология', 20)
SYNTH = Monster('Синтаксис', 30)
SEM = Monster('Семантика', 40)


# ______________________________________________window functions_____________________________________________________
# most of their names speak for their purposes


# a function that allows the player to choose a name for their character
def player_name(text_out):
    def button():
        name = info.field.get()
        PLAYER.name = name
        info.crash()
        # text_out is a line that contains a special symbol. this line is printed after the function stops
        # the special symbol is replaced (depending on what the player chooses) prior to that
        Q.appendleft(Label(f, fg='dimgrey', bg='bisque', font=20, wraplength=500, justify=LEFT,
                           text=f"{text_out.replace('$', name)}"))

    info = Window_class(size='350x150+500+100', title='Ввод', text='Имя...', field_for_input=True,
                        btn_list=([('Принять!', button)]))


# choose allies for one fight
def choose_your_fighter(fighters):
    global fighter1, fighter2, button_chosen
    button_chosen = 0
    fighter1 = ''
    fighter2 = ''

    def choose_lisa_for_fight():
        global fighter1, fighter2, button_chosen
        if button_chosen == 0:
            fighter1 = LISA
            button_chosen = 1

        elif button_chosen == 1:
            fighter2 = LISA
            if fighter1 != fighter2:
                button_chosen = 0
                fight_choice.crash()
                Q.appendleft(Label(f, fg='grey', bg='bisque', font=20, wraplength=500, justify=LEFT,
                                   text=f"{fighters.replace('$', f'{fighter1} и {fighter2}')}"))
            # checking that 2 allies aren't actually 1 character
            else:
                fight_choice.quest['text'] = 'Пожалуйста, выберите\nдругого персонажа'

    def choose_dan_for_fight():
        global fighter1, fighter2, button_chosen
        if button_chosen == 0:
            fighter1 = DAN
            button_chosen = 1

        elif button_chosen == 1:
            fighter2 = DAN
            if fighter1 != fighter2:
                button_chosen = 0
                fight_choice.crash()
                Q.appendleft(Label(f, fg='dimgrey', bg='bisque', font=20, wraplength=500, justify=LEFT,
                                   text=f"{fighters.replace('$', f'{fighter1} и {fighter2}')}"))
            else:
                fight_choice.quest['text'] = 'Пожалуйста, выберите\nдругого персонажа'

    def choose_fedya_for_fight():
        global fighter1, fighter2, button_chosen
        if button_chosen == 0:
            fighter1 = FEDYA
            button_chosen = 1

        elif button_chosen == 1:
            fighter2 = FEDYA
            if fighter1 != fighter2:
                button_chosen = 0
                fight_choice.crash()
                Q.appendleft(Label(f, fg='dimgrey', bg='bisque', font=20, wraplength=500, justify=LEFT,
                                   text=f"{fighters.replace('$', f'{fighter1} и {fighter2}')}"))
            else:
                fight_choice.quest['text'] = 'Пожалуйста, выберите\nдругого персонажа'

    def choose_monya_for_fight():
        global fighter1, fighter2, button_chosen
        if button_chosen == 0:
            fighter1 = MONYA
            button_chosen = 1

        elif button_chosen == 1:
            fighter2 = MONYA
            if fighter1 != fighter2:
                button_chosen = 0
                fight_choice.crash()
                Q.appendleft(Label(f, fg='dimgrey', bg='bisque', font=20, wraplength=500, justify=LEFT,
                                   text=f"{fighters.replace('$', f'{fighter1} и {fighter2}')}"))
            else:
                fight_choice.quest['text'] = 'Пожалуйста, выберите\nдругого персонажа'

    fight_choice = Window_class(size='500x190+500+100', title='Пора в бой!', text='Кого возьмешь в команду?',
                                btn_list=([('Лиза', choose_lisa_for_fight), ('Федя', choose_fedya_for_fight),
                                           ('Даня', choose_dan_for_fight), ('Моня', choose_monya_for_fight)]))


# choosing who will take action this turn (and who will be targeted)
def choose_active():
    global fighter1
    global fighter2
    global chosen

    def choose_fighter1_as_active():
        global chosen
        chosen = fighter1
        active_choice.crash()

    def choose_fighter2_as_active():
        global chosen
        chosen = fighter2
        active_choice.crash()

    def choose_player_as_active():
        global chosen
        chosen = PLAYER
        active_choice.crash()

    active_choice = Window_class(size='500x190', title='', text='Выберете персонажа,\nкоторый будет действовать',
                                 btn_list=([(fighter1.name, choose_fighter1_as_active),
                                            (fighter2.name, choose_fighter2_as_active),
                                            (PLAYER.name, choose_player_as_active)]))


# player's skills are the same as the ones of his friends. but they are nerfed
def choose_skill_for_player():
    global chosen_player_skill

    def choose_first_skill():
        global chosen_player_skill
        chosen_player_skill = PLAYER.skills[0]
        w.crash()

    def choose_second_skill():
        global chosen_player_skill
        chosen_player_skill = PLAYER.skills[1]
        w.crash()

    def choose_third_skill():
        global chosen_player_skill
        chosen_player_skill = PLAYER.skills[2]
        w.crash()

    def choose_fourth_skill():
        global chosen_player_skill
        chosen_player_skill = PLAYER.skills[3]
        w.crash()

    if len(PLAYER.skills) == 2:
        w = Window_class(size='500x190', title='', text='Выберете,\nчто вы будете делать',
                         btn_list=([(PLAYER.skills[0], choose_first_skill),
                                    (PLAYER.skills[1], choose_second_skill)]))
    elif len(PLAYER.skills) == 3:
        w = Window_class(size='500x190', title='', text='Выберете,\nчто вы будете делать',
                         btn_list=([(PLAYER.skills[0], choose_first_skill),
                                    (PLAYER.skills[1], choose_second_skill),
                                    (PLAYER.skills[2], choose_third_skill)]))
    else:
        w = Window_class(size='500x190', title='', text='Выберете,\nчто вы будете делать',
                         btn_list=([(PLAYER.skills[0], choose_first_skill),
                                    (PLAYER.skills[1], choose_second_skill),
                                    (PLAYER.skills[2], choose_third_skill),
                                    (PLAYER.skills[3], choose_fourth_skill)]))


# _________________________________________________interactions_______________________________________________________

def fedya_question():
    def fed_zdrv():
        FEDYA.utter('О, ты запомнил мое имя!')
        call.crash()

    def fed_privet():
        FEDYA.utter('Не называй меня так!*2*')
        call.crash()

    call = Window_class(size='500x190+500+100', title='Надо позвать Федю', text='Как позовёшь Федю?',
                        btn_list=([('Федя, привет!', fed_privet), ('Фердинанд, здравствуй!', fed_zdrv)]))


def answer_back():
    def sorry():
        FEDYA.utter('Ладно, проехали')
        answer.crash()

    def not_sorry():
        FEDYA.utter(f'Ну и иди лесом, {PLAYER.name}!')
        answer.crash()

    answer = Window_class(size='500x190+500+100', title='', text='Что ответить?',
                          btn_list=([('Прости, больше не буду', sorry), ('Всё равно будешь Федей', not_sorry)]))


# _________________________________________________endings________________________________________________________

def the_end(text, image):
    last_window = Toplevel()
    last_window.title("the end")
    last_window.geometry('350x500+500+100')
    last_window["bg"] = 'bisque'
    Label(last_window, text=text, bg='bisque', fg='darkgoldenrod',
          font=('Times New Roman', 18)).pack()
    img = PhotoImage(file=image)
    Label(last_window, image=img).pack()

    last_window.mainloop()


# _________________________________________________<BEGINNING________________________________________________________


# variables that allow the program to have phases
# this essential for the player to be able to affect the flow of thee game
# a phase is changed after every single choice made by player,
# not to run the program before it has the variables it needs
stage_fight = None
stage_save_story = 0
stage = 1


def STORY():
    global stage
    global stage_save_story
    global stage_fight
    # when we are in a fight
    if stage < 0:
        return
    # when the story is played. phases of story can't be repeated (stages of fight are cyclic)
    if stage == 1:
        tell('это история 4 ребят и вас')
        tell('это Лиза Андреева')
        LISA.utter('здравствуйте')
        tell('это Даня Михаэль')
        DAN.utter('давай вместе идти к мечте')
        tell('это Федя Сосся')
        FEDYA.utter("Я Фердинанд")
        tell('Ему не нравится, когда его называют Федей')
        tell('это Моня Мохская')
        MONYA.utter('йоу че как жизнь')
        tell('в первый день учебы Юрий Ландыш давал приветственную речь')
        YL.utter('здравствуйте детишки')
        YL.utter('надеюсь, у вас все будет хорошо')
        YL.utter('а если нет, моя дверь всегда открыта для вас')
        IB.utter('и моя. чая хватит на всех')
        tell('ваши однокурсники подошли познакомиться:@')
    elif stage == 2:
        # interaction
        tell('Подошёл Федя*1*')
    elif stage == 3:
        # choosing allies
        tell('Пора в бой!^1^')
    elif stage == 4:
        # player's character getting his skills from rising friendship with current allies
        tell(f'{fighter1} и вы стали ближе!')
        tell(f'{fighter2} и вы стали ближе!')
        fighter1.friendship_with_player += 1
        if fighter1.friendship_with_player == 1:
            PLAYER.heal += fighter1.heal // 2
            PLAYER.buff += fighter1.buff // 2
            PLAYER.shield += fighter1.shield // 2
            PLAYER.kill += fighter1.kill // 2
            PLAYER.skills.append(fighter1.skill)
        fighter2.friendship_with_player += 1
        if fighter2.friendship_with_player == 1:
            PLAYER.heal += fighter2.heal // 2
            PLAYER.buff += fighter2.buff // 2
            PLAYER.shield += fighter2.shield // 2
            PLAYER.kill += fighter2.kill // 2
            PLAYER.skills.append(fighter2.skill)
        # checking if an ally has special knowledge of this subject and informing the player
        if fighter1.morph == 1:
            fighter1.utter('Я чувствую себя так уверенно!')
        if fighter2.morph == 1:
            fighter2.utter('Я чувствую себя очень уверенно!')
        stage_save_story = stage + 1
        # for STORY not to run while the FIGHT is not done
        stage = -1
        stage_fight = 'friends take action'
        tell('Морфология наступает...')
        tell('Вы с друзьями переглядываетесь...^2^')
        tell('%1%')
        return
    elif stage == 5:
        tell('Вы победили!!')
        fighter1.utter("Уф, это было непросто...")
        fighter2.utter("Да уж, но мы показали этой морфологии, где аффиксы зимуют!")
        fighter1.utter(f"{PLAYER}, тебе ещё многому предстоит научиться")
        tell(f"{fighter1} похлопывает вас по спине")
        tell("Пока вы переводите дыхание после боя, к вам спешат Инна Бисер с Юрием Ландышем.")
        IB.utter("Браво, дорогие коллеги! Вы отлично справились!")
        YL.utter("Да, в честь этой небольшой победы заходите к нам пить чай с печеньками)")
    elif stage == 6:
        tell('Прошла неделя')
        tell('Внезапно вам объявили о предстоящем бое с синтаксисом')
    elif stage == 7:
        tell('Пора в бой!^1^')
    elif stage == 8:
        tell(f'{fighter1} и вы стали ближе!')
        tell(f'{fighter2} и вы стали ближе!')
        fighter1.friendship_with_player += 1
        if fighter1.friendship_with_player == 1:
            PLAYER.heal += fighter1.heal // 2
            PLAYER.buff += fighter1.buff // 2
            PLAYER.shield += fighter1.shield // 2
            PLAYER.kill += fighter1.kill // 2
            PLAYER.skills.append(fighter1.skill)
        fighter2.friendship_with_player += 1
        if fighter2.friendship_with_player == 1:
            PLAYER.heal += fighter2.heal // 2
            PLAYER.buff += fighter2.buff // 2
            PLAYER.shield += fighter2.shield // 2
            PLAYER.kill += fighter2.kill // 2
            PLAYER.skills.append(fighter2.skill)
        if fighter1.synth == 1:
            fighter1.utter('Я чувствую себя так уверенно!')
        if fighter2.synth == 1:
            fighter2.utter('Я чувствую себя очень уверенно!')
        stage_save_story = stage + 1
        stage = -1
        stage_fight = 'friends take action'
        tell('Синтаксис наступает...')
        tell('Вы с друзьями переглядываетесь...^2^')
        tell('%2%')
        return
    elif stage == 9:
        tell('Вы победили!!')
    elif stage == 10:
        tell('Только вы собрались отдохнуть, как дали новое задание')
        tell('На этот раз вам предстоит столкнуться с семантикой')
    elif stage == 11:
        tell('Пора в бой!^1^')
    elif stage == 12:
        tell(f'{fighter1} и вы стали ближе!')
        tell(f'{fighter2} и вы стали ближе!')
        fighter1.friendship_with_player += 1
        if fighter1.friendship_with_player == 1:
            PLAYER.heal += fighter1.heal // 2
            PLAYER.buff += fighter1.buff // 2
            PLAYER.shield += fighter1.shield // 2
            PLAYER.kill += fighter1.kill // 2
            PLAYER.skills.append(fighter1.skill)
        fighter2.friendship_with_player += 1
        if fighter2.friendship_with_player == 1:
            PLAYER.heal += fighter2.heal // 2
            PLAYER.buff += fighter2.buff // 2
            PLAYER.shield += fighter2.shield // 2
            PLAYER.kill += fighter2.kill // 2
            PLAYER.skills.append(fighter2.skill)
        if fighter1.sem == 1:
            fighter1.utter('Я чувствую себя так уверенно!')
        if fighter2.sem == 1:
            fighter2.utter('Я чувствую себя очень уверенно!')
        stage_save_story = stage + 1
        stage = -1
        stage_fight = 'friends take action'
        tell('Семантика наступает...')
        tell('Вы с друзьями переглядываетесь...^2^')
        tell('%3%')
        return
    elif stage == 13:
        tell('Вы победили!!')
        YL.utter("Поздравляю! Вы справились со всеми испытаниями")
        IB.utter('Непременно заходите к нам на чай с печеньками!')
        tell("конец игры~")
    stage += 1


# ___________________________________________________END>_____________________________________________________________
# Tkinter thingies - this causes the window to actually appear
# part of 'Тело' on our scheme
frm1.pack(fill="both", expand=True)
frm2.pack(anchor='s')
btn.pack(anchor='ne', padx=10, pady=10)
# causes the window to be adjustable
root.mainloop()
# ___________________________________________________<END_____________________________________________________________
