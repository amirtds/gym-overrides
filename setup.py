from setuptools import setup, find_packages

setup(
    name='gym_overrides',
    version='0.0.1',
    author='Amir Tadrisi',
    author_email='amirtds@gmail.com',
    license='MIT',
    description='Customizing The Gymnasium Open edX Instance Plugin',
    packages=find_packages(
        include=['gym_overrides', 'gym_overrides.*']
    ),
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'lms.djangoapp': [
            'gym_overrides = gym_overrides.apps:GymOverridesConfig',
        ],
},
)