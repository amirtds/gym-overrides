from xmodule.tabs import CourseTab, CourseTabList, key_checker
from lms.djangoapps.courseware.entrance_exams import user_can_skip_entrance_exam
from lms.djangoapps.courseware.access import has_access
from lms.djangoapps.courseware.tabs import _get_dynamic_tabs


def get_course_tab_list(prev_fn, user, course):
    """
    Retrieves the course tab list from xmodule.tabs and manipulates the set as necessary
    """
    xmodule_tab_list = CourseTabList.iterate_displayable(course, user=user)
    # Now that we've loaded the tabs for this course, perform the Entrance Exam work.
    # If the user has to take an entrance exam, we'll need to hide away all but the
    # "Courseware" tab. The tab is then renamed as "Entrance Exam".
    course_tab_list = []
    must_complete_ee = not user_can_skip_entrance_exam(user, course)
    for tab in xmodule_tab_list:
        if must_complete_ee:
            # Hide all of the tabs except for 'Courseware'
            # Rename 'Courseware' tab to 'Entrance Exam'
            if tab.type != 'courseware':
                continue
            tab.name = _("Entrance Exam")
            tab.title = _("Entrance Exam")
        if tab.type == 'static_tab' and tab.course_staff_only and \
                not bool(user and has_access(user, 'staff', course, course.id)):
            continue
        # Hide the progress tab
        if tab.type == 'progress':
            continue
        course_tab_list.append(tab)
    # Add in any dynamic tabs, i.e. those that are not persisted
    course_tab_list += _get_dynamic_tabs(course, user)
    # Sorting here because although the CourseTabPluginManager.get_tab_types function
    # does do sorting on priority, we only use it for getting the dynamic tabs.
    # We can't switch this function to just use the CourseTabPluginManager without
    # further investigation since CourseTabList.iterate_displayable returns
    # Static Tabs that are not returned by the CourseTabPluginManager.
    course_tab_list.sort(key=lambda tab: tab.priority or float('inf'))
    return course_tab_list