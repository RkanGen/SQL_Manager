# SQL_Manager

![image](https://github.com/user-attachments/assets/8ea87e2c-7c04-4d4c-9068-3e9e5a3045d3)

# Enhanced SQL Assistant 🤖

A powerful SQL query generator and database analysis tool built with Streamlit and Google's Gemini Pro. This application allows users to interact with their databases using natural language, generates optimized SQL queries, provides data visualizations, and offers intelligent insights.

## 🌟 Features

- **Natural Language to SQL**: Convert plain English questions into optimized SQL queries
- **Interactive Chat Interface**: User-friendly chat-based interface for database interactions
- **Smart Visualizations**: Automatic chart recommendations based on query results
- **Database Analysis**: Get insights and patterns from your data
- **Multiple Chart Types**: Support for bar, line, scatter, and pie charts
- **Optimized Queries**: Built-in query optimization suggestions
- **Error Handling**: Robust error handling and retry mechanisms
- **Responsive UI**: Modern, clean interface with customizable settings

## 🛠️ Prerequisites

- Python 3.8+
- MySQL/MariaDB database
- Google API key for Gemini Pro

## 📦 Installation

1. Clone the repository:
```bash
git clone https://github.com/RkanGen/SQL_Manager
cd sql_manager
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

## 📋 Requirements

Create a `requirements.txt` file with the following dependencies:
```
streamlit
python-dotenv
google-generativeai
langchain
langchain-community
plotly
pandas
pymysql
```

## ⚙️ Configuration

1. Create a `.env` file in the project root:
```env
GOOGLE_API_KEY=your_gemini_pro_api_key_here
```

2. Make sure your database credentials are ready:
- Host
- Username
- Password
- Database name

## 🚀 Usage

1. Start the application:
```bash
streamlit run app.py
```

2. Open your web browser and navigate to `http://localhost:8501`

3. In the sidebar:
   - Enter your database connection details
   - Click "Connect" to establish database connection
   - Toggle settings for visualizations and SQL query display

4. Start asking questions about your data in natural language!

## 💬 Example Queries

- "Show me total sales by product category"
- "What were the top 5 customers last month?"
- "Compare revenue between this year and last year"
- "Show me the trend of monthly orders"

## 🎯 Features in Detail

### Database Connection
- Supports MySQL/MariaDB databases
- Secure password handling
- Connection status indicators
- Database schema display

### Query Generation
- Context-aware query generation
- Support for complex analytical queries
- Query optimization suggestions
- Proper JOIN operations

### Data Visualization
- Automatic chart type recommendation
- Multiple visualization options:
  - Bar charts
  - Line charts
  - Scatter plots
  - Pie charts
- Customizable chart titles and axes

### Natural Language Processing
- Comprehensive response generation
- Trend analysis
- Pattern identification
- Follow-up suggestions

## ⚠️ Error Handling

The application includes robust error handling for:
- Database connection issues
- Query execution failures
- Invalid user inputs
- API rate limits
- Timeout scenarios

## 🔒 Security Considerations

- Database credentials are never stored
- Secure password input
- Environment variable usage for API keys
- Input validation and sanitization

## 🔄 Retry Mechanism

Built-in retry logic for:
- Database operations
- API calls
- Query execution

## 🎨 Customization

### Settings
- Toggle SQL query display
- Enable/disable visualizations
- Customize chart appearance
- Adjust retry parameters

### Visualization Options
- Chart type selection
- Color schemes
- Axis configurations
- Data aggregation options

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🐛 Known Issues

- Large dataset handling may require optimization
- Some complex queries might need manual optimization
- Visualization recommendations may need refinement for certain data types

## 🔜 Future Enhancements

- Support for additional database types
- More visualization options
- Advanced analytics features
- Export functionality
- Query history tracking
- Custom visualization templates

## 👥 Support

For support, please:
1. Check existing issues
2. Create a new issue with detailed information
3. Contact the maintainers

## 🙏 Acknowledgments

- Streamlit for the wonderful framework
- Google for the Gemini Pro API
- LangChain for the database utilities
- All contributors and users

---

