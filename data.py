from csv import writer
import os
import os.path


class Data:
	


	def __init__(self, num_assets):
		pass



	"""
	Resets data files for a fresh simulation run,
	"""
	def delete_files_at_start(self):
		if os.path.exists("supports.cvs"):
			os.remove("supports.cvs")	
		if os.path.exists("resistances.cvs"):
			os.remove("resistances.cvs")
		if os.path.exists("ohlc.cvs"):
			os.remove("ohlc.cvs")
		if os.path.exists("entry.cvs"):
			os.remove("entry.cvs")	



	"""
	Deletes specified files.
	Parameters:
		open_file (String): Holds open prices for Each security in play for each timeslot at a specified timeframe, throughout the duration of simulation.
		high_file (String): Holds high prices for Each security in play for each timeslot at a specified timeframe, throughout the duration of simulation.
		low_file (String): Holds low prices for Each security in play for each timeslot at a specified timeframe, throughout the duration of simulation.
		close_file (String): Holds close prices for Each security in play for each timeslot at a specified timeframe, throughout the duration of simulation.
		volume_file (String): Holds volume prices for Each security in play for each timeslot at a specified timeframe, throughout the duration of simulation.
	"""	
	def delete_files(self, open_file, high_file, low_file, close_file, volume_file):
		if os.path.exists(open_file):
			os.remove(open_file)
		if os.path.exists(high_file):
			os.remove(high_file)	
		if os.path.exists(low_file):
			os.remove(low_file)					
		if os.path.exists(close_file):
			os.remove(close_file)
		if os.path.exists(volume_file):
			os.remove(volume_file)			



	"""
	Creates a file for open prices, close prices, highs, lows, or volumes for all securities in play, for a given timeframe.
	Parameters:
		filename ("String"): Name of file.
		assets ([String]): A list of the securities in play sorted alphabetically by ticker symbol.
		times ([Int]): List of the time slots as dictated by limit.
		datas ([[Float]]): List of either opens, highs, lows, closes or volumes for all securites in play and all alloted time slots.
		limit (Int): Number of candlesticks specified.
	"""
	def create_data_file(self, filename, assets, times, datas, limit):
		file_exists = os.path.isfile(filename)

		fields = ['timeframe'] 
		for i in range(0, len(assets)):
			fields.append(assets[i])


		file_created = False
		trial = 0
		while((not file_created) and trial < 3):		
			try:

				with open(filename, 'a', newline='') as f_object:  #For the CSV file, create a file object 
					writer_object = writer(f_object) # Pass the CSV  file object to the writer() function
					if not file_exists:
						writer_object.writerow(fields) 			

				for i in range(0, limit):

					list_data=[times[i]]
					for j in range(0, len(datas[i])):
						list_data.append(datas[i][j])
	
					with open(filename, 'a', newline='') as f_object:  #For the CSV file, create a file object 
						writer_object = writer(f_object) #Pass the CSV  file object to the writer() function
						writer_object.writerow(list_data) #Result - a writer object # Pass the data in the list as an argument into the writerow() function
						f_object.close() #Close the file object	

				file_created = True

			except:# IOError:
				print("Could not create "+str(filename))
				file_created = False			



	"""
	Adds a row representing opens, highs, lows, closes, or volumes, for all securities in play, to their appropriate file.
		filename ("String"): Name of file.
		times ([pandas.Timestamp]): List of the time slots as dictated by limit.
		datas ([[Float]]): List of either opens, highs, lows, closes or volumes for all securites in play and all alloted time slots.	
	"""
	def add_row_to_data_file(self, filename, times, datas):
		file_exists = os.path.isfile(filename)

		list_data=[times[-1]]
		for j in range(0, len(datas[-1])):
			list_data.append(datas[-1][j])

		row_added = False
		trial = 0
		while((not row_added) and trial < 3):		
			try:

				with open(filename, 'a', newline='') as f_object:  #For the CSV file, create a file object 
					writer_object = writer(f_object) # Pass the CSV  file object to the writer() function
					writer_object.writerow(list_data)      # Result - a writer object # Pass the data in the list as an argument into the writerow() function
					f_object.close() # Close the file object

				row_added = True

			except:# IOError:
				print("Could not add row to "+str(filename))
				row_added = False



	"""
	Deletes a row from specified file name.
	Parameters:
		filename (String): Name of the file.
	"""
	def delete_last_row_from_data_file(self, filename):

		row_deleted = False
		trial = 0
		while((not row_deleted) and trial < 3):		
			try:

				f = open(filename, "r+")
				lines = f.readlines()
				lines.pop()
				f = open(filename, "w+")
				f.writelines(lines)	

				row_deleted = True

			except:# IOError:
				print("Could not delete frow from "+str(filename))
				row_deleted = False




	def create_data_files(self, assets, limit, times, opens, highs, lows, closes, volumes, open_file, high_file, low_file, close_file, volume_file):
		#Delete files 
		self.delete_files(open_file, high_file, low_file, close_file, volume_file)
		#Re-create the files
		self.create_data_file(open_file, assets, times, opens, limit)
		self.create_data_file(high_file, assets, times, highs, limit)
		self.create_data_file(low_file, assets, times, lows, limit)
		self.create_data_file(close_file, assets, times, closes, limit)
		self.create_data_file(volume_file, assets, times, volumes, limit)

			

	def add_row_to_data_files(self, times, opens, highs, lows, closes, volumes, open_file, high_file, low_file, close_file, volume_file):
		self.add_row_to_data_file(open_file, times, opens)
		self.add_row_to_data_file(high_file, times, highs)
		self.add_row_to_data_file(low_file, times, lows)
		self.add_row_to_data_file(close_file, times, closes)
		self.add_row_to_data_file(volume_file, times, volumes)		



	def delete_last_row_from_data_files(self, open_file, high_file, low_file, close_file, volume_file):
		self.delete_last_row_from_data_file(open_file)
		self.delete_last_row_from_data_file(high_file)
		self.delete_last_row_from_data_file(low_file)
		self.delete_last_row_from_data_file(close_file)
		self.delete_last_row_from_data_file(volume_file)	



	"""
	Retrieves last n rows from file where n is represented by limit.  Each row represents a timeslot for all securities in play, for the timeframe
	specified in the filename.
	Parameters:
		filename ("String"): Name of file.
		time_rows ([pandas.TimeStamp]):
		data_rows ([[Float]]): List of lists. Each nested list being a row obtained from the file specified, holding either opens, highs, lows, closes, volumes
		                       of all securities in question for a given minute.
	"""
	def get_rows_from_file(self, filename, time_rows, data_rows, limit):

		row_read = False
		trial = 0
		while((not row_read) and trial < 3):		
			try:

				#Open the file and get all the lines in a list
				with open(filename, 'r') as f_object:

					#Read all lines
					rows = f_object.readlines()
    
				#Remove the line feed code with strip ()
				#Convert strings to arrays separated by commas with split ()
				#Convert each element of the array from a string to a float type with map ()
				#rows_arr = [list(map(float, row.strip().split(','))) for row in rows[-limit:]]
				rows_arr = [list(row.strip().split(',')) for row in rows[-limit:]]

				time_arr = []

				for i in range(0, len(rows_arr)):
					time_arr.append(rows_arr[i][0])
					#Now remove time from array 
					del rows_arr[i][0]

				for i in range(0, len(rows_arr)):
					#Convert the timeless array to float
					rows_arr[i] = [float(x) for x in rows_arr[i]]

				return time_arr, rows_arr

			except:# IOError:
				print("Could not get row frow from "+str(filename))
				row_read = False

		return time_rows, data_rows #In case all trials fail	



	def get_rows_from_files(self, open_file, high_file, low_file, close_file, volume_file, time_rows, open_rows, high_rows, low_rows, close_rows, volume_rows, limit):
		time_arr, open_arr = self.get_rows_from_file(open_file, time_rows, open_rows, limit)
		time_arr, high_arr = self.get_rows_from_file(high_file, time_rows, high_rows, limit)
		time_arr, low_arr = self.get_rows_from_file(low_file, time_rows, low_rows, limit)
		time_arr, close_arr = self.get_rows_from_file(close_file, time_rows, close_rows, limit)
		time_arr, volume_arr = self.get_rows_from_file(volume_file, time_rows, volume_rows, limit)

		return time_arr, open_arr, high_arr, low_arr, close_arr, volume_arr


