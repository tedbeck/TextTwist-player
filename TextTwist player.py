# TextTwist automated player
# Can complete all anagrams by matching all permutations to a English corpus
# Program uses visual capture to identify letters through a root means square function

import sys, time, os
from itertools import permutations
from selenium import webdriver
from PIL import Image, ImageGrab

# loads image files for all letters A through Z
def build_letters():
    letters = []
    an_example = []
    for i in range(26):
        file = chr(i + 97) + '.png'
        screen = Image.open(os.path.join(r'c:\Users\Ted.Beck\Desktop\Stacks\letters\training\averages', file))
        for y in range(screen.size[1]):
            temp = []
            for x in range(screen.size[0]):
                temp.append(screen.getpixel((x, y)))
            an_example.append(temp)
        letters.append(an_example)
        an_example = []
    return letters

# calculates root mean square for a patch by comparing it to the loaded letters
def rms(matrix_1, matrix_2):
    rms = []
    # calculate pairwise squared differences
    for j in range(len(matrix_1)):
        temp = []
        for i in range(len(matrix_1[0])):
            pixel_1 = matrix_1[j][i][0] + matrix_1[j][i][1] + matrix_1[j][i][2]
            pixel_2 = matrix_2[j][i][0] + matrix_2[j][i][1] + matrix_2[j][i][2]
            temp.append((pixel_1 - pixel_2) ** 2)
        rms.append(temp)
    # sum result
    counter = 0
    for j in range(len(rms)):
        for i in range(len(rms[0])):
            counter += rms[j][i]
    # divide by element count
    counter = counter / (len(rms) * len(rms[0]))
    # take root
    counter = counter ** 0.5
    return counter

# training function to build the composite patches for all letters
# background of each patch can vary, so "average" pixel values were calculated to minimize the error function and increase accuracy
def training(letters):
    found_it = False
    i = 700
    j = 0
    origin = ()
    screen = ImageGrab.grab()
    # screen.show()
    # print('Grabbed screen.')
    while not(found_it):
        if (screen.getpixel((i, j)) == (255, 204, 0)):
            origin = (i, j)
            found_it = True
        else:
            j += 1
        if j >= screen.size[1]:
            j = 0
            i += 1
            if i >= screen.size[0]:
                found_it = True
    # print('Found orange.')
    # to find the letters, a specific color of orange in a line on the player's screen is used as the origin point
    true_origin = (origin[0] - 3, origin[1] - 75)
    patches = []
    for i in range(6):
        a_patch = []
        current_origin = (true_origin[0] + (i * 63), true_origin[1])
        for y in range(55):
            temp = []
            for x in range(63):
                temp.append(screen.getpixel((current_origin[0] + x, current_origin[1] + y)))
            a_patch.append(temp)
        patches.append(a_patch)
    print('Created patches.')
    # print('Testing RMS for first and last patch: ', rms(patches[0], patches[5]))
    # to create training examples - comment out once the unicorns (rare letters) are all found (also remove 'counter' variable from function call)
    # for i in range(6):
    #     temp = Image.new('RGB', (len(patches[i][0]), len(patches[i])))
    #     for y in range(len(patches[i])):
    #         for x in range(len(patches[i][0])):
    #             temp.putpixel((x, y), patches[i][y][x])
    #     filename = 'ex' + str(counter + i) + '.png'
    #     pathname = r'c:\Users\Ted.Beck\Desktop\Stacks\letters\training'
    #     temp.save(os.path.join(pathname, filename))
    # print('Saved patches.')
    # do rms for six current patches against 26 letter templates; function then returns six-character string equivalent
    print('Identifying letters.')
    # identifies the letters for that round by RMS function; function matches to the training example that scores lowest on the RMS function
    current_string = ''
    low_val = 100000000
    index = 0
    for i in range(6):
        for j in range(26):
            temp_val = rms(patches[i], letters[j])
            if temp_val < low_val:
                low_val = temp_val
                index = j
        current_string += chr(index + 97)
        low_val = 100000000
        index = 0
    print('Found: ', current_string)
    return current_string

# start up function to initiate web driver and load game
def start_up():
    driver = webdriver.Chrome(executable_path=r'c:\Users\Ted.Beck\AppData\Local\Programs\Python\Python35-32\selenium\webdriver\chromium\chromedriver.exe')
    driver.get('http://zone.msn.com/gameplayer/gameplayer.aspx?game=texttwist')
    time.sleep(30)
    return driver

#start up function to build dictionary; corpus was optimized for size by eliminating all words longer than six characters
def build_dict():
    all_words = []
    f = open('c://Users/Ted.Beck/Desktop/words_alpha.txt', 'r')
    for line in f:
        all_words.append(line[:-1])
    f.close()
    return all_words

# returns all possible permutations from letters in that round
def scramble(word):
    scrambled_words = []
    for i in range(3, len(word) + 1):
        for result in permutations(word, i):
            temp = ''
            for char in result:
                temp += char
            scrambled_words.append(temp)
    return scrambled_words

# matches all permuted words to the dictionary and returns matched words
def find_matches(dictionary, scrambled):
    results = []
    for word in scrambled:
        if word in dictionary:
            results.append(word)
    return results

def main():
    driver = start_up()
    print('Webdriver loaded.')
    all_words = build_dict()
    print('Dictionary built.')
    templates = build_letters()
    print('Templates loaded.')
    # counter = 0
    user_input = input('Type \'go\' to cycle, \'quit\' to end: ')
    # once program can read need to change while cycle to function on enter, and 'quit' to quit
    # main gaming cycle; reads state to see if the round has started, if so, if identifies the letters present
    # then creates all permutations, matches those to the dictionary, and then fires the matched words to the
    # game screen
    while user_input != 'quit':
        if (user_input != 'go'):
            print('Unprocessed response.')
        else:
            # training(counter)
            astring = training(templates)
            element = driver.find_element_by_id('form1')
            actions = webdriver.ActionChains(driver)
            actions.move_to_element(element)
            actions.click()
            actions.perform()
            scrambled_words = scramble(astring)
            print('Word scrambled.')
            results = find_matches(all_words, scrambled_words)
            print('Words matched and firing.')
            for word in results:
                word += '\n'
                actions.send_keys(word)
                actions.perform()
                actions.reset_actions()
        user_input = input('Type \'go\' to cycle, \'quit\' to end: ')
        # counter += 6
    garbage = input('Press enter to end...')
    driver.close()


if __name__ == "__main__":
    sys.exit(int(main() or 0))