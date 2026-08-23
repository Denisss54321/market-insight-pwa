"use client";

import { useEffect, useState } from "react";

interface WebSocketMessage {
  type: string;
  item_id: string;
  data: any;
  timestamp: string;
}

export default function Home() {
  const [connected, setConnected] = useState(false);
  const [messages, setMessages] = useState<WebSocketMessage[]>([]);
  const [apiUrl] = useState(process.env.NEXT_PUBLIC_API_URL || "ws://localhost:8000");

  useEffect(() => {
    const ws = new WebSocket(`${apiUrl}/ws`);

    ws.onopen = () => {
      setConnected(true);
      console.log("WebSocket подключен");
    };

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data) as WebSocketMessage;
      setMessages((prev) => [message, ...prev].slice(0, 50));
      console.log("Получено сообщение:", message);
    };

    ws.onerror = (error) => {
      console.error("WebSocket ошибка:", error);
    };

    ws.onclose = () => {
      setConnected(false);
      console.log("WebSocket отключен");
    };

    // Ping/pong для поддержания соединения
    const pingInterval = setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send("ping");
      }
    }, 30000);

    return () => {
      clearInterval(pingInterval);
      ws.close();
    };
  }, [apiUrl]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-8">
        <header className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
            Market Insight PWA
          </h1>
          <p className="text-gray-600 dark:text-gray-300">
            Анализ рынка Stalcraft в реальном времени
          </p>
          <div className="mt-4 flex items-center gap-2">
            <div className={`w-3 h-3 rounded-full ${connected ? "bg-green-500" : "bg-red-500"}`} />
            <span className="text-sm text-gray-600 dark:text-gray-300">
              {connected ? "Подключено" : "Отключено"}
            </span>
          </div>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              Статистика
            </h2>
            <div className="space-y-4">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Активные соединения</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {messages.length}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Последнее обновление</p>
                <p className="text-sm text-gray-900 dark:text-white">
                  {messages[0]?.timestamp || "Нет данных"}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              Последние события
            </h2>
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {messages.slice(0, 10).map((msg, index) => (
                <div key={index} className="text-sm">
                  <span className="font-medium text-blue-600 dark:text-blue-400">
                    {msg.type}
                  </span>
                  <span className="text-gray-600 dark:text-gray-400 ml-2">
                    {msg.item_id}
                  </span>
                </div>
              ))}
              {messages.length === 0 && (
                <p className="text-gray-500 dark:text-gray-400 text-sm">
                  Ожидание данных...
                </p>
              )}
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              Информация
            </h2>
            <div className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
              <p>• Централизованный коллектор данных</p>
              <p>• Real-time обновления через WebSocket</p>
              <p>• Оптимизация API запросов</p>
              <p>• PWA - работает офлайн</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
