# Election in Flask Python


**Software Description:**

This software is an election management system built using Python and Flask. It facilitates the process of managing elections, including candidate registration, voting, and result tallying. The system includes the following key components:

1. **Models (`election1/models.py`):**
   - **User**: Manages user relationships and roles.
   - **Dates**: Stores the start and end dates for elections.
   - **Votes**: Represents votes cast by users.
   - **Tokenlist**: Manages tokens used for voting.

2. **Forms (`election1/ballot/form.py`):**
   - **CandidateForm**: Form for candidate registration.
   - **Candidate_reportForm**: Form for generating candidate reports.
   - **OfficeForm**: Form for managing office titles and sort keys.
   - **ClassgrpForm**: Form for managing class or group names and sort keys.
   - **DatesForm**: Form for setting election start and end dates.

3. **Views (`election1/vote/view.py`):**
   - **Voting Process**: Handles the voting process, including token validation, candidate selection, and vote submission.
   - **Token Management**: Generates and manages voting tokens.
   - **Results**: Displays election results and allows for result searches.

4. **Utilities (`election1/utils.py`):**
   - **Token Generation**: Utility functions for generating and validating tokens.

5. **Database**: Utilizes SQLAlchemy for database interactions, managing relationships between users, candidates, votes, and tokens.

The system ensures secure and efficient election management, providing a user-friendly interface for administrators and voters. It includes features like token-based voting, real-time vote tallying, and detailed result reporting.

---

## Getting Started

### Dependencies
 
* Python: The primary programming language used.
* Flask: A web framework for building the web application.
* SQLAlchemy: An ORM (Object Relational Mapper) for database interactions.
* Flask-WTF: Flask integration with WTForms for form handling.
* WTForms-Alchemy: Adds additional functionality to WTForms, such as model-based forms.
* XlsxWriter: A library for creating Excel files.
* Pathlib: A module for handling filesystem paths.
* Datetime: A module for manipulating dates and times.
* Collections: A module providing alternatives to Python's general-purpose built-in containers.
* SQLAlchemy-Utils: Provides various utility functions for SQLAlchemy.

### Installing

1  Clone the Repository:
 
* git clone <repository_url>
* cd <repository_directory>

2  Create a virtual Environment:

* python -m venv venv

3  Activate the Virtual Environment:

*  On Windows
    *  venv\Scripts\Activate

*  On macOS/Linux
    *  source venv/bin/activate
 
4  Install Dependencies:
*  pip install -r requirements  


### Executing program

* How to run the program
* Step-by-step bullets
```
code blocks for commands
```

## Help

Any advise for common problems or issues.
```
command to run if program contains helper info
```

## Authors

Contributors names and contact info

ex. Dominique Pizzie  
ex. [@DomPizzie](https://twitter.com/dompizzie)

## Version History

* 0.2
    * Various bug fixes and optimizations
    * See [commit change]() or See [release history]()
* 0.1
    * Initial Release

## License

This project is licensed under the [NAME HERE] License - see the LICENSE.md file for details

## Acknowledgments

Inspiration, code snippets, etc.
* [awesome-readme](https://github.com/matiassingers/awesome-readme)
* [PurpleBooth](https://gist.github.com/PurpleBooth/109311bb0361f32d87a2)
* [dbader](https://github.com/dbader/readme-template)
* [zenorocha](https://gist.github.com/zenorocha/4526327)
* [fvcproductions](https://gist.github.com/fvcproductions/1bfc2d4aecb01a834b46)
