# Maps canonical skill names to a couple of learning resources each.
# Used to turn the "missing skills" list into something actionable.
# Not every skill in the dictionary has an entry yet - we fall back to
# a generic search link when there's nothing here.

SKILL_RESOURCES = {
    'Python': [
        ('Official tutorial', 'https://docs.python.org/3/tutorial/'),
        ('Real Python', 'https://realpython.com/'),
    ],
    'JavaScript': [
        ('MDN JavaScript Guide', 'https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide'),
        ('javascript.info', 'https://javascript.info/'),
    ],
    'TypeScript': [
        ('TS Handbook', 'https://www.typescriptlang.org/docs/handbook/intro.html'),
    ],
    'Java': [
        ('Oracle Java Tutorials', 'https://docs.oracle.com/javase/tutorial/'),
    ],
    'C++': [
        ('learncpp.com', 'https://www.learncpp.com/'),
        ('cppreference', 'https://en.cppreference.com/w/'),
    ],
    'C#': [
        ('Microsoft C# docs', 'https://learn.microsoft.com/en-us/dotnet/csharp/'),
    ],
    'C': [
        ('Modern C (free book)', 'https://gustedt.gitlabpages.inria.fr/modern-c/'),
    ],
    'Go': [
        ('Tour of Go', 'https://go.dev/tour/'),
    ],
    'Rust': [
        ('The Rust Book', 'https://doc.rust-lang.org/book/'),
    ],
    'Ruby': [
        ('Ruby docs', 'https://www.ruby-lang.org/en/documentation/'),
    ],
    'PHP': [
        ('PHP manual', 'https://www.php.net/manual/en/'),
    ],
    'Swift': [
        ('Swift docs', 'https://www.swift.org/documentation/'),
    ],
    'Kotlin': [
        ('Kotlin docs', 'https://kotlinlang.org/docs/home.html'),
    ],
    'SQL': [
        ('SQLBolt interactive lessons', 'https://sqlbolt.com/'),
        ('Mode SQL tutorial', 'https://mode.com/sql-tutorial/'),
    ],
    'PostgreSQL': [
        ('PostgreSQL docs', 'https://www.postgresql.org/docs/'),
    ],
    'MySQL': [
        ('MySQL docs', 'https://dev.mysql.com/doc/'),
    ],
    'MongoDB': [
        ('MongoDB University', 'https://learn.mongodb.com/'),
    ],
    'Redis': [
        ('Redis University', 'https://university.redis.com/'),
    ],
    'React': [
        ('React docs', 'https://react.dev/learn'),
    ],
    'Vue.js': [
        ('Vue docs', 'https://vuejs.org/guide/introduction.html'),
    ],
    'Angular': [
        ('Angular docs', 'https://angular.dev/'),
    ],
    'Node.js': [
        ('Node.js docs', 'https://nodejs.org/en/learn/getting-started/introduction-to-nodejs'),
    ],
    'Django': [
        ('Django tutorial', 'https://docs.djangoproject.com/en/stable/intro/tutorial01/'),
    ],
    'Flask': [
        ('Flask tutorial', 'https://flask.palletsprojects.com/en/stable/tutorial/'),
    ],
    'HTML': [
        ('MDN HTML', 'https://developer.mozilla.org/en-US/docs/Web/HTML'),
    ],
    'CSS': [
        ('MDN CSS', 'https://developer.mozilla.org/en-US/docs/Web/CSS'),
        ('CSS Tricks', 'https://css-tricks.com/'),
    ],
    'Git': [
        ('Pro Git book (free)', 'https://git-scm.com/book/en/v2'),
    ],
    'Docker': [
        ('Docker Get Started', 'https://docs.docker.com/get-started/'),
    ],
    'Kubernetes': [
        ('Kubernetes basics', 'https://kubernetes.io/docs/tutorials/kubernetes-basics/'),
    ],
    'AWS': [
        ('AWS Skill Builder (free)', 'https://skillbuilder.aws/'),
    ],
    'Azure': [
        ('Microsoft Learn - Azure', 'https://learn.microsoft.com/en-us/training/azure/'),
    ],
    'Google Cloud Platform': [
        ('Google Cloud Skills Boost', 'https://www.cloudskillsboost.google/'),
    ],
    'Linux': [
        ('Linux Journey', 'https://linuxjourney.com/'),
    ],
    'Bash': [
        ('Bash guide', 'https://mywiki.wooledge.org/BashGuide'),
    ],
    'Machine Learning': [
        ('Andrew Ng course', 'https://www.coursera.org/specializations/machine-learning-introduction'),
        ('scikit-learn user guide', 'https://scikit-learn.org/stable/user_guide.html'),
    ],
    'Deep Learning': [
        ('Deep Learning Specialization', 'https://www.coursera.org/specializations/deep-learning'),
    ],
    'TensorFlow': [
        ('TensorFlow tutorials', 'https://www.tensorflow.org/tutorials'),
    ],
    'PyTorch': [
        ('PyTorch tutorials', 'https://pytorch.org/tutorials/'),
    ],
    'Pandas': [
        ('Pandas user guide', 'https://pandas.pydata.org/docs/user_guide/index.html'),
    ],
    'NumPy': [
        ('NumPy quickstart', 'https://numpy.org/doc/stable/user/quickstart.html'),
    ],
    'Data Analysis': [
        ('Kaggle Learn', 'https://www.kaggle.com/learn'),
    ],
    'Tableau': [
        ('Tableau training', 'https://www.tableau.com/learn/training'),
    ],
    'Power BI': [
        ('Microsoft Learn - Power BI', 'https://learn.microsoft.com/en-us/training/powerplatform/power-bi'),
    ],
    'Excel': [
        ('ExcelJet', 'https://exceljet.net/'),
    ],
    'REST APIs': [
        ('RESTful API tutorial', 'https://restfulapi.net/'),
    ],
    'GraphQL': [
        ('How to GraphQL', 'https://www.howtographql.com/'),
    ],
    'Agile': [
        ('Atlassian Agile coach', 'https://www.atlassian.com/agile'),
    ],
    'Scrum': [
        ('Scrum Guide', 'https://scrumguides.org/'),
    ],
    'Jira': [
        ('Jira tutorials', 'https://www.atlassian.com/software/jira/guides'),
    ],
    'Figma': [
        ('Figma Academy', 'https://www.figma.com/academy/'),
    ],
    'UI/UX Design': [
        ('NN/g articles', 'https://www.nngroup.com/articles/'),
    ],
    'Cybersecurity': [
        ('TryHackMe', 'https://tryhackme.com/'),
    ],
    'Networking': [
        ('Cisco NetAcad', 'https://www.netacad.com/'),
    ],
}


def get_resources(skill):
    """
    Look up resources for a skill. If we don't have any specific ones,
    return a single fallback Google search link so the UI always has
    something to show.
    """
    if skill in SKILL_RESOURCES:
        return SKILL_RESOURCES[skill]

    query = skill.replace(' ', '+')
    return [
        ('Search for tutorials', f'https://www.google.com/search?q=learn+{query}+tutorial'),
    ]
