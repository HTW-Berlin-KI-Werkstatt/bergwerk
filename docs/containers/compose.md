# Docker Compose Configuration

The `docker-compose.yaml` file orchestrates the various services that make up the Bergwerk application. It establishes a network for all services, manages dependencies, and initiates each component in the correct order. The following services are defined within this configuration:

- **Bergwerk Admin**: Provides an admin panel for the entire Bergwerk system
- **Bergwerk Wiki**: Hosts the wiki-based content management system, where chatbot data is stored and maintained.
- **Bergwerk API**: Provides access to the wiki, allowing for import/export operations and data management.
- **Bergwerk Cron**: Schedules tasks to automatically create and update wiki pages from conversation logs in the database.
- **Bergwerk Database**: A MySQL database used to store wiki and conversation data.
- **Bergwerk SocketIO**: Manages real-time communication with the Rasa Webchat plugin, enabling interactive chat features.
- **Bergwerk Caddy**: Acts as a reverse HTTP(S) proxy, providing SSL termination and serving both the Wiki and API components.

This configuration ensures that all services interact seamlessly, with dependencies managed and connections secured. Using Docker Compose simplifies deployment and scaling, making Bergwerk easy to set up and operate.


## docker-compose.yaml

```yaml
--8<-- "./docker-compose.yaml"
```