import setuptools

"""
    1.打包pip库：
        python3 setup.py sdist bdist_wheel
    2.上传测试服务器
        python3 -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*
    3.上传正式服务器
        python3 -m twine upload dist/*
    4.用户名：tianyejun

"""
projectDiff = "projectdiff"
projectDiffVersion = "1.0.9"
projectDiffDescription = "比较项目的差异",
projectDiff_console_scripts = "projectdiff = merge_project_diff.merge_project_files:main"

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    # 库名
    name=projectDiff,
    # 版本号
    version=projectDiffVersion,
    # 作者
    author="XiaoTian",
    # 作者邮箱
    author_email="1961993790@qq.com",
    # 简述
    description=projectDiffDescription,
    # 详细描述
    long_description=long_description,
    # README.md中描述的语法（一般为markdown）
    long_description_content_type="text/markdown",
    # 该项目的GitHub地址
    url="https://github.com/pypa/sampleproject",
    # 使用setuptools.find_packages()即可，这个是方便以后我们给库拓展新功能的
    packages=setuptools.find_packages(),
    include_package_data=True,
    # 指定该库依赖的Python版本、license、操作系统之类的
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    # entry_points将Python模块转变为命令行
    entry_points={
        'console_scripts': [
            projectDiff_console_scripts
        ]
    },
    # install_requires=[  # 你的库依赖的第三方库（也可以指定版本）eg:lxml>= 4.9.1
    #     "lxml >= 4.9.1"
    # ]

)
