#!/usr/env python
'''
A module for converting a CSV file into a SQLite database table for a survey.
'''

import argparse
import csv
import itertools


# Utility Functions #
#####################


# NOTE: A lot of times, people will create a library of related utilities,
#       but we'll worry about organizing this later.

# A standard python recipe
def take(n, iterable):
    '''Return first n items of the iterable as a list'''
    return list(itertools.islice(iterable, n))


def table(iterable, maxrows=None):
    '''Create a two dimensional matrix containing all the rows
    from the iterable table until maxrows is reached.

    This will not consume any more than maxrows from the iterator.
    '''
    if maxrows is None:
        return list(iterable)
    else:
        return take(maxrows, iterable)


# Models #
##########

# NOTE: Many of these models are dependent on the format of the survey data we are using.
#
# If we wanted to use this code to convert any CSV into a database, we would have to
# restructure our models to represent tables, columns, rows, etc.
#
# I only put this note here, so you can see how a MVC project might be laid out

# I got this from stack exchange to make printing a survey nicer:
# http://stackoverflow.com/questions/1036409/recursively-convert-python-object-graph-to-dictionary
def todict(obj, classkey=None):
    '''Convert an object graph into a dictionary for reference or printing'''
    if isinstance(obj, dict):
        for k in obj.keys():
            obj[k] = todict(obj[k], classkey)
        return obj
    elif hasattr(obj, "__iter__"):
        return [todict(v, classkey) for v in obj]
    elif hasattr(obj, "__dict__"):
        data = dict([(key, todict(value, classkey))
            for key, value in obj.__dict__.iteritems()
            if not callable(value) and not key.startswith('_')])
        if classkey is not None and hasattr(obj, "__class__"):
            data[classkey] = obj.__class__.__name__
        return data
    else:
        return obj

class BaseModel(object):
    '''A base class for all model classes to inherit from.'''
    def __str__(self):
        '''Recursively convert all attributes into a dictionary'''
        import pprint
        return pprint.pformat(self.todict())
    def todict(self):
        return todict(self)

class SurveyResponse(BaseModel):
    '''A model of a response in a survey.'''
    def __init__(self):
        # TODO: Decide what meta data we want to store about a response
        self.id = None
        self.ip_address = ''
        self.timestamp = ''
        self.duplicate = False
        self.timespent = 0
        # A map (aka dict) of question ids -> str(answer)
        # A string is sufficient model for an answer, so we don't need a model class for it
        self.answers = {}

class SurveyChoice(BaseModel):
    '''A model of an answer to a single question in a response.'''
    def __init__(self):
        self.id = None
        self.text = ''

class SurveyQuestion(BaseModel):
    '''A model of a question in a survey.'''

    MULTIPLE_CHOICE     = 'multiple choice'
    CHECKBOX_LIST       = 'checkbox list'
    DROPDOWN_FREETEXT   = 'dropdown with freetext other'

    def __init__(self):
        self.id = None
        self.type = None
        self.text = ''
        self.choices = []

class Survey(BaseModel):
    '''A model to represent a single table survey.'''
    def __init__(self):
        self.id = None
        self.title = ''
        self.comment = ''
        self.questions = []
        self.responses = []


# Controllers #
###############

# NOTE: Currently there is one controller. We may want to abstract what it is that
#       a SurveyService does, so that we can have different implementations that
#       would, for example, persist the Survey to a database rather than just spit
#       out the SQL commands to construct a database with a single "Response" table.

class SurveyService:
    '''A service for parsing and populating Surveys'''

    def __init__(self):
        pass

    def parseFile(self, path, survey, dialect=csv.Sniffer()):
        '''Converts a CSV file into a Survey.'''
        with open(path, 'rb') as f:
            reader = csv.reader(f, dialect=dialect)
            self.parse(reader, survey)

    def parse(self, reader, survey):
        '''Converts an iterable table representation of a survey into a Survey object.'''
        self._parse_metadata(reader, survey)
        self._parse_questions(reader, survey)
        #self._parse_responses(reader, survey)

    def _parse_metadata(self, iterable, survey):
        '''Populates table header meta data into a Survey.

        Takes only the first cell of the first two rows of the iterable table
        to be the title and comment respectively.

        '''
        # There are only 2 rows that define the meta data for the survey
        matrix = take(2, iterable)
        survey.title = matrix[0][0]
        survey.comment = matrix[1][0]

    def _parse_questions(self, iterable, survey):
        '''Populates the colmodel of the survey with column data.'''
        # There are only 2 rows that define the column names (aka the questions)
        matrix = take(2, iterable)
        # First parse the answer choices
        for i in range(17, len(matrix[0])):
            question_column = False
            if matrix[0][i] != '':
                question_column = True
                question = SurveyQuestion()
                question.text = matrix[0][i]
                # We'll assume multiple choice unless we detect a choice
                question.type = SurveyQuestion.MULTIPLE_CHOICE
                survey.questions.append(question)
            if matrix[1][i] != '':
                if question_column:
                    # There is a question in this column
                    survey.questions[-1].type = SurveyQuestion.CHECKBOX_LIST
                elif survey.questions[-1].type is not SurveyQuestion.CHECKBOX_LIST:
                    # There is NO question in this column
                    # There was NO choice in the same column as the question
                    assert matrix[1][i].lower() == 'other'
                    survey.questions[-1].type = SurveyQuestion.DROPDOWN_FREETEXT
                    # TODO: Do we need the 'other' choice?
                    continue
                choice = SurveyChoice()
                choice.text = matrix[1][i]
                survey.questions[-1].choices.append(choice)

    def _parse_responses(self, iterable, survey, limit=None):
        '''Populates the responses of the survey with the remaining rows in the data.'''
        matrix = table(iterable, maxrows=limit)
        # Parse all the remaining rows
        for row in matrix:
            response = SurveyResponse()
            # TODO: Need to determine which columns relate to the response meta data
            #       and which are answers.

    # NOTE: The order of arguments is flipped to conserve the chronological order
    #       of the operation:
    #
    #           survey --( dump SQL to )-> file
    def dump(self, survey, writable):
        '''Dump a survey as SQL into a writable object, such as a file.'''
        pass


# Views #
#########

# NOTE: We may at some point want a more interactive experience, that code would go here

# Command Line Interface #

# TODO: Create unit tests instead of running the script each time and reading the debug statements
def main(argv):
    parser = argparse.ArgumentParser(description='Parse a spreadsheet into a database.')
    parser.add_argument('files', metavar='files', nargs='+',
                        help='the CSV files to convert')
    # TODO: Update these to reflect what we are using this for
    parser.add_argument('-d', dest='delim', default=' ',
                        help='the delimiter between values on the same row')
    parser.add_argument('-o', dest='output',
                        help='the destination sqlite dump file')
    args = parser.parse_args(argv)

    surveys = []
    surveyService = SurveyService()
    # NOTE: I like to put CLI related import statements inside the function,
    #       so there is no overhead if importing this module into something else
    #       that does not use the command line main() function.
    from glob import glob

    for filename in (filename for path in args.files for filename in glob(path)):
        print("Creating survey from '%s' ..." % filename)
        survey = Survey()
        surveyService.parseFile(filename, survey)
        surveys.append(survey)
    # Now let's see what we got
    print("Resulting survey objects:")
    print(surveys[0])


if __name__ == '__main__':
    import sys
    main(sys.argv[1:])

