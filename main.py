from bisect import bisect
from random import random, choices, choice
from re import findall
from os import listdir, path, system

class MarkovChain:
    
    def __init__(self,order:int):
        """
        Creates a model for Markov Chain mathemetical system that experiences transitions 
        from one state to another according to certain probabilistic rules
        
        Arguments:
        ----------
        - order {int} : order of the system, preferred [1-4] 
        """

        self._order = order
        self._model = dict()

    class State:
        def __init__(self):
            """
            State Property
            """
            self.count = 0  
            self.properties = dict()
            
        def __str__(self):
                return str([f'{i} : {p/self.count}' for i,p in self.properties.items()])

        def add(self,data:list):
            """
            Adds new property to the state and adjusts counters
            """
            if self.count > 0:
                if data in self.properties:
                    self.properties[data] += 1
                else:
                    self.properties[data] = 1
            else:
                self.properties[data] = 1 
            self.count += 1

    def train(self,data:str) -> None:
        """
        Trains the model with given data

        Arguments:
        ----------
        - data {str} : input string data
        """

        # ---------- ERROR CHECK ----------
        if not data or data == '':
            raise Exception(f"InputError: Valid data must be provided to train the model!")

        # ---------- PREPROCESSING ----------
        # - makes all chars lowercase
        # - using regex, some punctuations are discarded
        # - all words and punctuations (, . ? ! ;) are seperated into a list

        data = data.lower() 
        data = findall(pattern="[\w']+|[.,!?;]",string=data)

        # ---------- TRAINING MODEL ----------
        for i in range(0,len(data)):
            main_val = []
            # from a value by given order
            for j in range(i, i + self._order):
                main_val.append(data[j])
            # add to the model
            main_val = tuple(main_val)
            if main_val not in self._model:
                self._model[main_val] = self.State()
            # add next value to the state
            if i != len(data) - 2 * self._order:
                next_val = []
                for k in range(i + self._order, i + 2 * self._order):
                    next_val.append(data[k])
                self._model[main_val].add(tuple(next_val))
            # end of the data
            else: break

    def generate(self,data:str=None,max_sentence:int=1) -> list:
        """
        Generates a synthetic string with given prior input string data using Markov Chain model

        Arguments:
        - data {str} : input string data 
        - max_sentence {int} : number of sentences
        """

        if not data:
            # random start data to be selected
            data = ['.' for x in range(0,self._order)]
            while data[0] in ['!',',','.','?']:
                data = choice(list(self._model.keys()))
        else:
            data = findall(pattern="[\w']+|[.,!?;]",string=data.lower())
            if len(data) != self._order:
                raise Exception(f"InputError: Length of the given prior input string data is not: {self._order}")
            
        state = tuple(data) # converting to tuple to have hashable identity

        result = []

        # ---------- PRIOR INPUT ----------
        result.extend(list(state))
        
        # ---------- GENERATION ----------
        while max_sentence > 0 and state in self._model:
            next_states, next_probabilities = [], []
            state_stats = self._model[state]

            for t,c in state_stats.properties.items():
                next_states.append(t)
                next_probabilities.append(c/state_stats.count) # probability = count/total

            if len(next_states) > 0:
                state:tuple = choices(next_states,next_probabilities)[0]
                for s in state:
                    if s in ['.','!','?']: max_sentence -= 1
                result.extend(list(state))
            else:
                break

        # ---------- IMPROVEMENT ----------
        if result[-1] not in ['.','!','?']:
            k = 1
            while k < len(result):
                if result[-k] in ['.','!','?']:
                    result = result[:-k+1]
                    break
                k += 1

        return result

    def statistics(self):
        """
        Prints statistics of the Markov Chain model
        """
        pcount = 0
        for i, p in self._model.items():
            print(f'{i} : {p}')
            pcount += len(p.properties)
        print(f'State count: {len(self._model)}, total transitions: {pcount}')

def file_to_str(f) -> str:
    """
    Reads lines from a file then modifies them accordingly

    Arguments:
    - f {file} : input file
    """
    result = ""
    raw_data = f.readlines()
    for line in raw_data:
        if line[-1] not in [',','.','!','?',';']:
            result += line.replace('\n','.')
        else:
            result += line.replace('\n', ' ')
    return result

def create_lyrics(data:list) -> str:
    """
    Turn list of strings into a proper one lyric string
    
    Arguments:
    data {list} - list of strings
    """

    all_puncs = [',','.','!','?',';']

    result = ""
    new_line = True

    for s in data:
        if new_line:
            result += s.capitalize()
            new_line = False
        else:
            if s in all_puncs:
                if s != ',':
                    result += s + '\n'
                    new_line = True
                else:
                    result += s 
            else:
                result += ' ' + s

    if result[-1] not in ['.','!','?']:
            k = 1
            while k < len(result):
                if result[-k] in ['.','!','?']:
                    result = result[:-k+1]
                    break
                k += 1

    return result

def main():
    """
    Main program function
    """
    # ---------- INPUT ----------
    order = -1
    while order not in range(1,10):
        order = input("Type the order of the Markov Chain Model's order [1-10]: ")
        if order in ['q','quit','escape']: return
        try: order = int(order)
        except: 
            print('Input must be a number between 1 and 10, try again.')
            order = -1
    
    sentences = -1
    while not sentences > 0:
        sentences = input("Type the number of sentences to be generated from Markov Chain Model [>0]: ")
        if sentences in ['q','quit']: return
        try: sentences = int(sentences)
        except:
            print('Input must be a number bigger than 0, try again.')
            sentences = -1

    source = ""
    while source not in ['eminem','pink floyd','queen']:
        source = input("Type name of the group/artist to train Markov Chain Model ['eminem','pink floyd','queen']: ")
        if source in ['q','quit']: return
        try: source = source.lower()
        except: 
            print("Input must be 'eminem', 'pink floyd' or 'queen', try again.")
            source = ""

    # ---------- TRAINING ----------
    try:
        model = MarkovChain(order=order) # model creation

        if source == 'eminem': source_path = PATH_EMINEM
        elif source == 'pink floyd': source_path = PATH_PINK_FLOYD
        elif source == 'queen': source_path = PATH_QUEEN

        data = ""
        for name in listdir(source_path):
            with open(path.join(source_path,name),'r') as f:
                data += file_to_str(f)

        model.train(data=data) # model training
        #model.statistics()
    except Exception as e:
        print(e)
        return

    # ---------- GENERATION ----------
    while True:
        try:
            initials = input(f"Type words for the first state of the model according to selected order ({order}) [order == number of words], type nothing for random: ")
            if initials == 'q': return
            elif initials == "": # random choice
                result = model.generate(max_sentence=sentences)
            else: # given initial state
                result = model.generate(data=initials,max_sentence=sentences)
            print(f"{'-'*25}\n{create_lyrics(data=result)}\n{'-'*25}")
        except Exception as e:
            print(e)

if __name__ == "__main__":

    # ---------- DEFINITIONS ----------
    PATH_EMINEM = ".\lyrics\eminem\\"
    PATH_PINK_FLOYD = ".\lyrics\pink floyd\\"
    PATH_QUEEN = ".\lyrics\queen\\"

    main()