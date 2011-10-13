#!/usr/env python
'''
A module for converting a CSV file into a SQLite database table for a survey.
'''

import argparse
import csv
import itertools

from glob import glob

# From a recipe
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


class BaseModel:
	'''A base class for all model classes to inherit from.'''
	def __str__(self):
		return str(dict((str(k), str(v)) for k, v in vars(self).items()))

class SurveyResponse(BaseModel):
	'''A model of a response in a survey.'''
	def __init__(self):
		# TODO: This could be simplified to only store answers to questions
		self.id = None
		self.ip_address = ''
		self.timestamp = ''
		self.duplicate = False
		self.timespent = 0

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

class SimpleSurvey(BaseModel):
	'''A model to represent a single table survey.'''
	def __init__(self):
		self.id = None
		self.title = ''
		self.comment = ''
		self.questions = []
		self.responses = []


class SimpleSurveyService:
	'''Converts files into a SimpleSurvey.

	'''
	def __init__(self):
		pass

	def parseFile(self, path, survey, dialect=csv.Sniffer()):
		with open(path, 'rb') as file:
			reader = csv.reader(file, dialect=dialect)
			self.parseMetaData(reader, survey)
			self.parseQuestions(reader, survey)

	def parseMetaData(self, iterable, survey, maxrows=2):
		'''Populates CSV header meta data into a SimpleSurvey.
		
		Takes only the first cell of the first two rows of the iterable table
		to be the title and comment respectively.

		'''
		matrix = take(maxrows, iterable)
		survey.title = matrix[0][0]
		survey.comment = matrix[1][0]

	def parseQuestions(self, iterable, survey, maxrows=None):
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

	def parseResponses(self, iterable, survey, maxrows=None):
		'''Populates the colmodel of the survey with column data.'''
		matrix = table(iterable, maxrows=maxrows)
		# Parse all the remaining rows
		for row in matrix:
			response = SurveyResponse()
			# TODO: Need to differential between response and row


class SmartSurveyService:
	'''To implement when Coleman isn't a pussy ass bitch'''
	pass


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
	parser = SimpleSurveyService()
	for filename in (filename for path in args.files for filename in glob(path)):
		print("Creating survey from '%s' ..." % filename)
		survey = SimpleSurvey()
		parser.parseFile(filename, survey)
		surveys.append(survey)
	# Now let's see what we got
	print("Resulting survey objects:")
	for s in surveys:
		print(str(s))


if __name__ == '__main__':
    import sys
    main(sys.argv[1:])

