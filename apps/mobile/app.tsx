import axios from 'axios';

// Importante: No mobile, use o IP da sua máquina local ou a URL de produção.
// Se estiver usando Expo, pode usar: process.env.EXPO_PUBLIC_API_URL
const BASE_URL = process.env.EXPO_PUBLIC_API_URL || 'http://192.168.1.X:8000';

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para injetar o Token JWT automaticamente nas requisições
api.interceptors.request.use(
  async (config) => {
    // Exemplo: buscar token do storage local (AsyncStorage/SecureStore)
    // const token = await AsyncStorage.getItem('@token');
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`;
    // }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor para tratar erros globais (ex: token expirado - 401)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Lógica para deslogar o usuário ou renovar o token
      console.log('Sessão expirada. Faça login novamente.');
    }
    return Promise.reject(error);
  }
);

export default api;
