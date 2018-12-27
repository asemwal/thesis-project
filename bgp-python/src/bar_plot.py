import sys, os, time, thread, numpy, operator,json
sys.path.append('/opt/local/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages')
sys.path.append( str(os.getcwd()) )
import requests
from BGP_data_database import BGP_Data_Database
from datetime import datetime
from printer import Printer
import random

import plotly
import plotly.plotly as py
import plotly.graph_objs as go

class Bar_Plot:
	file_name = "temp" + str( random.randint(1000000,9999999) )
	title = None
	title_font_size = None
	legend_font_size = None
	legend_position = None

	bar_mode = 'group'
	width = None
	height = None
	auto_size = True

	delta_tick = None
	auto_tick = True

	show_legend = False;

	color_y_1 = None
	color_y_2 = None
	color_y_3 = None

	axis_x_name = None
	axis_y_name = None

	legend_x = None
	legend_y_1 = None
	legend_y_2 = None
	legend_y_3 = None

	data_x = None
	data_y_1 = None
	data_y_2 = None
	data_y_3 = None

	P = None

	def __init__( self, P = None ):
		if P is not None:
			self.P = P
		else:
			self.P = Printer()
			self.P.write( "[WARNING] Bar_Plot : __init__ : P is None", color = 'yellow', attrs = ['bold'] )

		self.P.write( "Bar_Plot: Loading...", color = 'cyan', attrs=['bold'] )
		#plotly.tools.set_credentials_file(username='Floader', api_key='Irf3uQQlXy2iDbFvntfr')
		plotly.tools.set_credentials_file(username='Floader1', api_key='TNGa7pdd7rA8DKAw8Cxa')
		#plotly.tools.set_credentials_file(username='Floader2', api_key='XDlXqb4sOk53LNKQBQFR')
		
	def reset( self ):
		self.file_name = "temp" + str( random.randint(1000000,9999999) )
		self.title = None
		self.title_font_size = None
		self.legend_font_size = None
		self.legend_position = None

		self.bar_mode = 'group'
		self.width = None
		self.height = None
		self.auto_size = True

		self.delta_tick = None
		self.auto_tick = True

		self.show_legend = False

		self.color_y_1 = None
		self.color_y_2 = None
		self.color_y_3 = None

		self.axis_x_name = None
		self.axis_y_name = None

		self.legend_x = None
		self.legend_y_1 = None
		self.legend_y_2 = None
		self.legend_y_3 = None

		self.data_x = None
		self.data_y_1 = None
		self.data_y_2 = None
		self.data_y_3 = None

	def set_parameters( self, title = None, color_y_1 = None, color_y_2 = None, color_y_3 = None, legend_y_1 = None, legend_y_2 = None, legend_y_3 = None, data_x = None, data_y_1 = None, data_y_2 = None, data_y_3 = None, 
							  axis_x_name = None, axis_y_name = None, title_font_size = None, bar_mode = None, width = None, height = None, delta_tick = None, legend_font_size = None, file_name = None, legend_position = None ):
			
		if legend_position is not None:
			self.legend_position = legend_position

		if file_name is not None:
			self.file_name = file_name

		if title is not None:
			self.title = title

		if legend_font_size is not None:
			self.legend_font_size = legend_font_size

		if color_y_1 is not None:
			self.color_y_1 = color_y_1

		if color_y_2 is not None:
			self.color_y_2 = color_y_2

		if color_y_3 is not None:
			self.color_y_3 = color_y_3

		if legend_y_1 is not None:
			self.legend_y_1 = legend_y_1
			self.show_legend = True;
			
		if legend_y_2 is not None:
			self.legend_y_2 = legend_y_2
			self.show_legend = True;

		if legend_y_3 is not None:
			self.legend_y_3 = legend_y_3
			self.show_legend = True;
			
		if data_x is not None:
			self.data_x = data_x
			
		if data_y_1 is not None:
			self.data_y_1 = data_y_1
			
		if data_y_2 is not None:
			self.data_y_2 = data_y_2

		if data_y_3 is not None:
			self.data_y_3 = data_y_3

		if axis_x_name is not None:
			self.axis_x_name = axis_x_name

		if axis_y_name is not None:
			self.axis_y_name = axis_y_name

		if title_font_size is not None:
			self.title_font_size = title_font_size

		if width is not None:
			self.width = width
			self.auto_size = False

		if height is not None:
			self.height = height
			self.auto_size = False

		if delta_tick is not None:
			self.delta_tick = delta_tick
			self.auto_tick = False

		if bar_mode is not None:
			self.bar_mode = bar_mode

	def set_file_name( self, file_name = None ):
		self.file_name = file_name

	def set_bar_mode( self, bar_mode = None ):
		self.bar_mode = bar_mode

	def set_legend_font_size( self, legend_font_size = None ):
		self.legend_font_size = legend_font_size

	def set_width( self, width = None ):
		self.width = width
		self.auto_size = False

	def set_height( self, height = None ):
		self.height = height
		self.auto_size = False

	def set_delta_tick( self, delta_tick = None ):
		self.delta_tick = delta_tick
		self.auto_tick = False

	def set_title( self, title = None ):
		self.title = title

	def set_title_font_size( self, title_font_size = None ):
		self.title_font_size = title_font_size

	def set_color_y_1( self, color_y_1 = None ):
		self.color_y_1 = color_y_1

	def set_color_y_2( self, color_y_2 = None ):
		self.color_y_2 = color_y_2

	def set_color_y_3( self, color_y_2 = None ):
		self.color_y_3 = color_y_3

	def set_legend_y( self, legend_y_1 = None, legend_y_2 = None, legend_y_3 = None ):
		if legend_y_1 is not None:
			self.legend_y_1 = legend_y_1
			self.show_legend = True;

		if legend_y_2 is not None:
			self.legend_y_2 = legend_y_2
			self.show_legend = True;

		if legend_y_3 is not None:
			self.legend_y_3 = legend_y_3
			self.show_legend = True;

	def set_legend_y_1( self, legend_y_1 = None ):
		self.legend_y_1 = legend_y_1
		self.show_legend = True;

	def set_legend_y_2( self, legend_y_2 = None ):
		self.legend_y_2 = legend_y_2
		self.show_legend = True;

	def set_legend_y_3( self, legend_y_3 = None ):
		self.legend_y_3 = legend_y_3
		self.show_legend = True;

	def set_data_x( self, data_x = None ):
		self.data_x = data_x

	def set_data( self, data_x = None, data_y_1 = None, data_y_2 = None, data_y_3 = None ):
		if data_x is not None:
			self.data_x = data_x
			
		if data_y_1 is not None:
			self.data_y_1 = data_y_1

		if data_y_2 is not None:
			self.data_y_2 = data_y_2

		if data_y_3 is not None:
			self.data_y_3 = data_y_3

	def set_data_y_1( self, data_y_1 = None ):
		self.data_y_1 = data_y_1

	def set_data_y_2( self, data_y_2 = None ):
		self.data_y_2 = data_y_2

	def set_axis_x_name( self, axis_x_name = None ):
		self.axis_x_name = axis_x_name

	def set_axis_y_name( self, axis_y_name = None ):
		self.axis_y_name = axis_y_name

	def set_legend_position( self, legend_position = None ):
		self.legend_position = legend_position

	def create_plot( self ):
		trace1 = go.Bar(
		    x = self.data_x,
		    y = self.data_y_1,
		    name = self.legend_y_1,
		    marker = dict( 
		    	color = self.color_y_1),
		)

		trace2 = go.Bar(
		    x = self.data_x,
		    y = self.data_y_2,
		    name = self.legend_y_2,
		    marker =dict(
		        color = self.color_y_2),
		)

		trace3 = go.Bar(
		    x = self.data_x,
		    y = self.data_y_3,
		    name = self.legend_y_3,
		    marker =dict(
		        color = self.color_y_3),
		)

		if self.data_y_3 is not None:
			data = [trace1, trace2, trace3]
		elif self.data_y_2 is not None:
			data = [trace1, trace2]
		else:
			data = [trace1]

		layout = go.Layout(
			autosize = self.auto_size,
			width = self.width,
			height = self.height,
		    barmode=self.bar_mode,
		    showlegend=self.show_legend,
		    titlefont = dict( size=self.title_font_size ),
		   	legend=dict( xanchor = "center", x= 0.5,
		   				 font=dict( size = self.legend_font_size ) ),
		    title = self.title,
		    xaxis = dict( title = self.axis_x_name, color=self.color_y_1, tickangle=90),   
		    yaxis = dict( title = self.axis_y_name, autotick=self.auto_tick, dtick=self.delta_tick ),
		    margin = dict( b = 160 ),
		)

		fig = go.Figure(data=data, layout=layout)
		py.plot(fig, filename=self.file_name )



		