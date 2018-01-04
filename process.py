import pyscreenshot as ImageGrab
import datetime
import pdb

def parse_input(body):
    return print_body(body)

def print_body(body):
    if (body):
        stripped = body[0:len(body)-3]
        question = "".join([(s.content + " ") for s in stripped])
        print(question)

        options = [body[-3].content,body[-2].content,body[-1].content]  

        for choice, a in zip(['A','B','C'], options):
            print(choice + ". " + a)

        return question, options

def screenshot():
    # im = ImageGrab.grab(bbox=(0,148,495,468))
    im = ImageGrab.grab(bbox=(0,220,562,520))
    now = datetime.datetime.now()
    id = now.strftime("%Y-%m-%d%H:%M")
    filename = "images/{}.png".format(id)
    im.save(filename)
    return filename

