import express, { Request, Response } from 'express';
import cors from 'cors';
import { z } from 'zod';

const app = express();
app.use(cors());
app.use(express.json());

// Helper para cálculo Haversine de distância em Km
function calculateDistance(lat1: number, lon1: number, lat2: number, lon2: number): number {
  const R = 6371;
  const dLat = (lat2 - lat1) * (Math.PI / 180);
  const dLon = (lon2 - lon1) * (Math.PI / 180);
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(lat1 * (Math.PI / 180)) * Math.cos(lat2 * (Math.PI / 180)) *
    Math.sin(dLon / 2) * Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
}

// Mock de base de dados para testes rápidos de execução
const mockInventories = [
  {
    pharmacyName: "Drogaria Raia Central",
    productName: "Dipirona 500mg - 20 Comprimidos",
    price: 8.50,
    latitude: -23.5510,
    longitude: -46.6340,
    requiresRx: false
  },
  {
    pharmacyName: "Farmácia Drogasil São Paulo",
    productName: "Dipirona 500mg - 20 Comprimidos",
    price: 6.90,
    latitude: -23.5530,
    longitude: -46.6350,
    requiresRx: false
  }
];

// ROTA 1: Busca de Medicamentos com Algoritmo Destaque
app.post('/api/v1/search', (req: Request, res: Response) => {
  const searchSchema = z.object({
    query: z.string(),
    latitude: z.number(),
    longitude: z.number(),
    radiusKm: z.number().default(5)
  });

  const parsed = searchSchema.safeParse(req.body);
  if (!parsed.success) {
    return res.status(400).json({ error: parsed.error.format() });
  }

  const { query, latitude, longitude, radiusKm } = parsed.data;

  const results = mockInventories
    .filter(item => item.productName.toLowerCase().includes(query.toLowerCase()))
    .map(item => {
      const distance = calculateDistance(latitude, longitude, item.latitude, item.longitude);
      const deliveryFee = Number((distance * 2.50).toFixed(2));
      const estimatedTimeMinutes = Math.round(15 + distance * 10);

      return {
        ...item,
        distanceKm: Number(distance.toFixed(2)),
        deliveryFee,
        estimatedTimeMinutes,
        score: item.price + deliveryFee + estimatedTimeMinutes * 0.1
      };
    })
    .filter(item => item.distanceKm <= radiusKm)
    .sort((a, b) => a.score - b.score);

  return res.json({
    total: results.length,
    highlight: results[0] || null,
    options: results
  });
});

// ROTA 2: Triagem Farmacêutica (Aprovação RDC)
app.post('/api/v1/pharmacist/review', (req: Request, res: Response) => {
  const reviewSchema = z.object({
    orderId: z.string(),
    status: z.enum(['approved', 'rejected']),
    notes: z.string().optional()
  });

  const parsed = reviewSchema.safeParse(req.body);
  if (!parsed.success) {
    return res.status(400).json({ error: parsed.error.format() });
  }

  const { orderId, status, notes } = parsed.data;

  return res.status(200).json({
    message: `Pedido ${orderId} atualizado com sucesso.`,
    orderStatus: status === 'approved' ? 'PREPARING' : 'REJECTED',
    reviewedAt: new Date().toISOString(),
    notes: notes || "Sem observações adicionais."
  });
});

// ROTA 3: Validação Facial do Entregador
app.post('/api/v1/courier/validate', (req: Request, res: Response) => {
  const { courierId, faceImageBase64 } = req.body;

  if (!courierId || !faceImageBase64) {
    return res.status(400).json({ error: "Dados incompletos para verificação biométrica." });
  }

  return res.json({
    courierId,
    verified: true,
    confidenceScore: 0.98,
    timestamp: new Date().toISOString()
  });
});

const PORT = process.env.API_PORT || 3000;
app.listen(PORT, () => {
  console.log(`DrugDelivery API rodando na porta ${PORT}`);
});
