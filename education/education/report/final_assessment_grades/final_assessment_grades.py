# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


from collections import defaultdict

import frappe
from frappe import _

from education.education.report.course_wise_assessment_report.course_wise_assessment_report import (
    get_chart_data, get_formatted_result)


def execute(filters=None):
	columns, data, grades = [], [], []
	args = frappe._dict()
	course_wise_analysis = defaultdict(dict)

	args["academic_year"] = filters.get("academic_year")
	assessment_group = args["assessment_group"] = filters.get("assessment_group")

	student_group = filters.get("student_group")
	args.students = frappe.get_all("Students Group Student", {
		"parent": student_group
	}, ["student"])

	values = get_formatted_result(args, get_course=True)
	assessment_result = values.get("assessment_result")
	course_dict = values.get("course_dict")

	for result in assessment_result:
		data.append({
			"student": result["student"],
			"student_name": result["student_name"]
		})

	for student in args.students:
		if student_details.get(student):
			student_row = {}
			student_row["student"] = student
			student_row["student_name"] = student_details[student]
			for course in course_dict:
				scrub_course = frappe.scrub(course)
				if assessment_group in assessment_result[student][course]:
					student_row["grade_" + scrub_course] = assessment_result[student][course][
						assessment_group
					]["Total Score"]["grade"]
					student_row["score_" + scrub_course] = assessment_result[student][course][
						assessment_group
					]["Total Score"]["score"]

					# create the list of possible grades
					if student_row["grade_" + scrub_course] not in grades:
						grades.append(student_row["grade_" + scrub_course])

					# create the dict of for gradewise analysis
					if student_row["grade_" + scrub_course] not in course_wise_analysis[course]:
						course_wise_analysis[course][student_row["grade_" + scrub_course]] = 1
					else:
						course_wise_analysis[course][student_row["grade_" + scrub_course]] += 1

			data.append(student_row)

	course_list = [d for d in course_dict]
	columns = get_column(course_dict)
	chart = get_chart_data(grades, course_list, course_wise_analysis)
	return columns, data, None, chart


def get_column(course_dict):
	columns = [
		{
			"fieldname": "student",
			"label": _("Student ID"),
			"fieldtype": "Link",
			"options": "Student",
			"width": 80,
		},
		{
			"fieldname": "student_name",
			"label": _("Student Name"),
			"fieldtype": "Data",
			"width": 150,
		},
		{
			"fieldname": "assessment_group",
			"label": _("Assessment Group"),
			"fieldtype": "Link",
			"width": 30
		}
	]
	for course in course_dict:
		columns.append(
			{
				"fieldname": "grade_" + frappe.scrub(course),
				"label": course,
				"fieldtype": "Data",
				"width": 100,
			}
		)
		columns.append(
			{
				"fieldname": "score_" + frappe.scrub(course),
				"label": "Score(" + str(course_dict[course]) + ")",
				"fieldtype": "Float",
				"width": 100,
			}
		)

	return columns
