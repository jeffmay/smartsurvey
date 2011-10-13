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

class BaseModel:
	'''A base class for all model classes to inherit from.'''
	def __str__(self):
        '''Recursively convert all attributes into a dictionary'''
        # TODO: Fix this, because it doesn't work
		return str(dict((str(k), str(v)) for k, v in vars(self).items()))

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
	def __init__(self):
		self.id = None
		self.type = ''
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
		with open(path, 'rb') as file:
			reader = csv.reader(file, dialect=dialect)
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
		matrix = take(2, iterable)
		survey.title = matrix[0][0]
		survey.comment = matrix[1][0]

	def _parse_questions(self, iterable, survey):
		'''Populates the colmodel of the survey with column data.'''
		matrix = table(iterable, maxrows=maxrows)
		# First parse the answers
		for i in range(len(matrix[0])):
			if matrix[0][i] != '':
				print("COLUMN: %s" % matrix[0][i])
				question = SurveyQuestion()
				question.text = matrix[0][i]
				survey.questions.append(question)
				# Increment the current question index
			if matrix[1][i] != '':
				print("CHOICE: %s" % matrix[1][i])
				choice = SurveyChoice()
				choice.text = matrix[1][i]
				# Add choice to the current question
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
def main(args):
	parser = argparse.ArgumentParser(description='Parse a spreadsheet into a database.')
	parser.add_argument('files', metavar='N', type=str, nargs='+',
                        help='the CSV files to convert')
	parser.add_argument('-d', dest='delim', default=' ',
						help='the destination file (automatically append .sql)')
	parser.add_argument('-o', dest='output', action='store_const',
						const=lambda filename: filename if filename.endswith('.sql') else filename + '.sql',
						help='the destination file (automatically append .sql)')
	args = parser.parse_args(args)

	surveys = []
	parser = SurveyService()
    # NOTE: I like to put CLI related import statements inside the function,
    #       so there is no overhead if importing this module into something else
    #       that does not use the command line main() function.
    from glob import glob
	for filename in (filename for path in args.files for filename in glob(path)):
		print("Creating survey from '%s' ..." % filename)
		survey = Survey()
		parser.parseFile(filename, survey)
		surveys.append(survey)
	# Now let's see what we got
	print("Resulting survey objects:")
	for s in surveys:
		print(str(s))


if __name__ == '__main__':
    import sys
    main(sys.argv[1:])

