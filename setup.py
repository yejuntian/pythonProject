import setuptools

"""

    1.打包pip库：
        python3 setup.py sdist bdist_wheel
    2.上传测试服务器
        python3 -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*
    3.上传正式服务器
        python3 -m twine upload dist/*
     3.1 上传到公司私服如下：
          python3 -m twine upload -r nexus dist/*
        
      3.2 install 命令：
          pip3 install vestpackage -i https://nexus.adsconflux.xyz/repository/pypi-hosted/simple --trusted-host https://nexus.adsconflux.xyz/ --upgrade
    
    4.测试服务器地址
        https://test.pypi.org/project/
    5.正式服务器地址
        https://pypi.org/project/
    6.用户名：tianyejun

"""
# 比较项目差异
projectDiff = "projectdiff"
projectDiffVersion = "1.1.0"
projectDiffDescription = "比较项目的差异",
projectDiff_console_scripts = f"{projectDiff} = merge_project_diff.merge_project_files:main"
# 马甲包
vestpackage = "vestpackage"
vestPackageVersion = "1.2.4"
vestPackageDescription = "马甲包",
vestPackage_console_scripts = f"{vestpackage} = vestpackage.replace_package:main"
# whatsapp 转gbwhatsapp
convertPackage = "convertgb"
convertPackageVersion = "1.1.2"
convertPackageDescription = "",
convertPackage_console_scripts = f"{convertPackage} = gbwhatsapp.__main__:main"
# 处理git修改文件
gitDiffPackage = "gitdiff"
gitDiffVersion = "1.0.1"
gitDiffDescription = "处理git修改文件",
gitDiff_console_scripts = f"{gitDiffPackage} = git_diff.__main__:main"
# androidx->androidy
convertAndroidYPackage = "convertandroidy"
convertAndroidYVersion = "1.0.1"
convertAndroidYDescription = "androidx->androidy",
convertAndroidY_console_scripts = f"{convertAndroidYPackage} = androidx_2_androidy.convert_androidy:main"
# support->supporty
convertSupportYPackage = "convertsupporty"
convertSupportYVersion = "1.0.0"
convertSupportYDescription = "support->supporty",
convertSupportY_console_scripts = f"{convertSupportYPackage} = support_2_supporty.convert_supporty:main"
# public.xml排序
publicSortPackage = "publicsort"
publicSortVersion = "1.0.0"
publicSortDescription = "public.xml排序",
publicSort_console_scripts = f"{publicSortPackage} = public_sort.public_sort:main"
# 生成gb diff
gbDiff = "gbdiff"
gbDiffVersion = "0.0.2"
gbDiffDescription = "生成gbdiff",
gbDiff_console_scripts = f"{gbDiff} = makeGBDiff.__main__:main"
# jenkens打包apk
pkApk = "pkapk"
pkApkVersion = "0.0.1"
pkApkDescription = "打包apk",
pkApk_console_scripts = f"{pkApk} = packageApk.packageApk:packageApk"

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    # 库名
    name=vestpackage,
    # 版本号
    version=vestPackageVersion,
    # 作者
    author="XiaoTian",
    # 作者邮箱
    author_email="1961993790@qq.com",
    # 简述
    description=vestPackageDescription,
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
            vestPackage_console_scripts
        ]
    },
    # install_requires=[  # 你的库依赖的第三方库（也可以指定版本）eg:lxml>= 4.9.1
    #     "lxml >= 4.9.1"
    # ]

)
