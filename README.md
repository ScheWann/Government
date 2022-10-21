# Government
> Sorry for the irreparable loss of all the code due to computer replacement, but I have provided most of the application information of the project

# Demo
<img alt="" src="./images/display.jpg">

# Introduction
> The project uses Vue.js + Flask + Echarts + DataV to implement all projects
<h3>Vue</h3>
Vue.js, as a progressive framework that has been developed day by day, can realize data binding and grouping of responses, and use simple APIs to build data-driven web interfaces. Single-page applications can refresh the page locally, without having to request every page jump. All data and dom.

<h4> The documents about Vue.js could be checked in https://vuejs.org/guide/introduction.html </h4>

<h3>Echarts</h3>
ECharts is a commercial-grade data chart, a pure Javascript chart library, which can run smoothly on PC and mobile devices, and is compatible with most current browsers (IE6/7/8/9/10/11, chrome, firefox, Safari, etc.), the bottom layer relies on the lightweight Canvas class library ZRender, providing intuitive, vivid, interactive, highly customizable data visualization charts

<h4> The documents about Flask could be checked in https://flask.palletsprojects.com/en/2.2.x/ </h4>

<h3>Flask</h3>
Flask is a "micro" framework for web development based on Python. The form of micro-framework gives developers more choices. The purpose of using Flask in this project is to provide a JSON data interface for the front end. Since the server program uses Flask, the Flask project team provides the Flask-SqlAlchemy extension and is highly linked to SqlAlchemy, which greatly facilitates the development of the Flask server program.

<h4> The documents about Echarts.js could be checked in https://echarts.apache.org/handbook/en/get-started/ </h4>

<h3>DataV</h3>
DataV is a Vue-based data visualization component library that provides SVG borders and decorations to enhance the visual effect of the page

<h4> The documents about DataV could be checked in https://github.com/DataV-Team/Datav </h4>

# backend/excel_crawler
> This is the core part of this project. It is used to crawl the complex excel tables

# Deficiencies in the system
- The system still has flaws in data acquisition and cannot obtain all data. For example, some provinces do not provide downloads of statistical yearbooks. Because the older xlrd library is used when crawling the statistical yearbook, because the latest openpyxl supports the latest xlsx format, and with the gradual elimination of the xp system from various office scenarios, the old file format of Microsoft office suite is no longer Applicable to the current environment. If the format of the statistical yearbook is changed in the future, the specific program of the current crawler needs to be rewritten, but the availability of openpyxl is very high, and the use of the new library will greatly improve the accuracy and maintainability of the crawler, although due to the characteristics of this library, the file loading may be more xlrd takes longer.
- For example:
  
  This is part of the code of the current crawling algorithm:
  ```
  ifself.wb.xf_list[self.tb.cell_xf_index(rx,0)].backdround.pattern_colour_index==44
  ```
  The significance of this part is to verify whether the current row is the row where the column header is located. The principle is to determine whether the background color of the current row is blue. It can be seen that the positioning of the cell position in the first half is very complicated and unintuitive, and the '44' at the end of the line is even more unclear. 
  
  But with the new library you can change to:
  ```
  if sele.tb[f’A{rx}’].fill.start_color==colors.Blue:
  ```
  Obviously, compared with the above, it is more concise: use the positioning method of excel (ie column-row combination, format string in the figure), and the color is preset by the openpyxl library, which can be called directly.