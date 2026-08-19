import React, { useState } from 'react';
import {
  StyleSheet,
  Text,
  View,
  TextInput,
  TouchableOpacity,
  FlatList,
  SafeAreaView,
  StatusBar
} from 'react-native';

interface SearchResult {
  pharmacyName: string;
  productName: string;
  price: number;
  deliveryFee: number;
  estimatedTimeMinutes: number;
  distanceKm: number;
  requiresRx: boolean;
}

export default function App() {
  const [query, setQuery] = useState('Dipirona');
  const [highlight, setHighlight] = useState<SearchResult | null>({
    pharmacyName: "Farmácia Drogasil São Paulo",
    productName: "Dipirona 500mg - 20 Comprimidos",
    price: 6.90,
    deliveryFee: 3.50,
    estimatedTimeMinutes: 25,
    distanceKm: 1.4,
    requiresRx: false
  });

  const [options, setOptions] = useState<SearchResult[]>([
    {
      pharmacyName: "Drogaria Raia Central",
      productName: "Dipirona 500mg - 20 Comprimidos",
      price: 8.50,
      deliveryFee: 2.50,
      estimatedTimeMinutes: 30,
      distanceKm: 0.8,
      requiresRx: false
    }
  ]);

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#00A86B" />

      {/* Header Verde Drogasil/Raia */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>🌿 DrugDelivery</Text>
        <Text style={styles.headerSubtitle}>Entregas Rápidas & Validação Farmacêutica</Text>

        <View style={styles.searchContainer}>
          <TextInput
            style={styles.searchInput}
            placeholder="Buscar medicamento (ex: DIPIRONA)"
            value={query}
            onChangeText={setQuery}
            placeholderTextColor="#888"
          />
          <TouchableOpacity style={styles.searchButton}>
            <Text style={styles.searchButtonText}>Buscar</Text>
          </TouchableOpacity>
        </View>
      </View>

      <View style={styles.content}>
        {/* Card em Destaque */}
        {highlight && (
          <View style={styles.highlightCard}>
            <View style={styles.badgeGroup}>
              <Text style={styles.badgeBest}>⭐ MELHOR OFERTA</Text>
              <Text style={styles.badgeSpeed}>⚡ ENTREGA RÁPIDA</Text>
            </View>

            <Text style={styles.productTitle}>{highlight.productName}</Text>
            <Text style={styles.pharmacyName}>{highlight.pharmacyName}</Text>

            <View style={styles.detailsRow}>
              <Text style={styles.price}>R$ {highlight.price.toFixed(2)}</Text>
              <Text style={styles.deliveryText}>
                Frete: R$ {highlight.deliveryFee.toFixed(2)} • {highlight.estimatedTimeMinutes} min
              </Text>
            </View>

            <TouchableOpacity style={styles.buyButton}>
              <Text style={styles.buyButtonText}>Adicionar ao Carrinho</Text>
            </TouchableOpacity>
          </View>
        )}

        <Text style={styles.sectionTitle}>Outras Opções na Região</Text>

        {/* Lista de Outras Opções */}
        <FlatList
          data={options}
          keyExtractor={(item, index) => index.toString()}
          renderItem={({ item }) => (
            <View style={styles.itemCard}>
              <View style={styles.itemHeader}>
                <Text style={styles.itemPharmacy}>{item.pharmacyName}</Text>
                <Text style={styles.itemDistance}>{item.distanceKm} km</Text>
              </View>
              <Text style={styles.itemPrice}>R$ {item.price.toFixed(2)}</Text>
              <Text style={styles.itemSubtext}>
                Entrega: R$ {item.deliveryFee.toFixed(2)} ({item.estimatedTimeMinutes} min)
              </Text>
            </View>
          )}
        />
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F9FAFB' },
  header: { backgroundColor: '#00A86B', padding: 20, borderBottomLeftRadius: 16, borderBottomRightRadius: 16 },
  headerTitle: { fontSize: 24, fontWeight: 'bold', color: '#FFF' },
  headerSubtitle: { fontSize: 13, color: '#E6F4EA', marginBottom: 15 },
  searchContainer: { flexDirection: 'row', gap: 10 },
  searchInput: { flex: 1, backgroundColor: '#FFF', borderRadius: 8, paddingHorizontal: 12, height: 44, fontSize: 14 },
  searchButton: { backgroundColor: '#008C5C', justifyContent: 'center', paddingHorizontal: 15, borderRadius: 8 },
  searchButtonText: { color: '#FFF', fontWeight: 'bold' },
  content: { flex: 1, padding: 16 },
  highlightCard: { backgroundColor: '#FFF', borderRadius: 12, padding: 16, borderLeftWidth: 6, borderLeftColor: '#00A86B', elevation: 3, marginBottom: 20 },
  badgeGroup: { flexDirection: 'row', gap: 8, marginBottom: 8 },
  badgeBest: { backgroundColor: '#FEF3C7', color: '#D97706', fontSize: 10, fontWeight: 'bold', padding: 4, borderRadius: 4 },
  badgeSpeed: { backgroundColor: '#D1FAE5', color: '#065F46', fontSize: 10, fontWeight: 'bold', padding: 4, borderRadius: 4 },
  productTitle: { fontSize: 16, fontWeight: 'bold', color: '#111827' },
  pharmacyName: { fontSize: 13, color: '#4B5563', marginBottom: 10 },
  detailsRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 },
  price: { fontSize: 20, fontWeight: 'bold', color: '#00A86B' },
  deliveryText: { fontSize: 12, color: '#6B7280' },
  buyButton: { backgroundColor: '#00A86B', borderRadius: 8, paddingVertical: 10, alignItems: 'center' },
  buyButtonText: { color: '#FFF', fontWeight: 'bold' },
  sectionTitle: { fontSize: 16, fontWeight: 'bold', color: '#111827', marginBottom: 10 },
  itemCard: { backgroundColor: '#FFF', borderRadius: 8, padding: 12, marginBottom: 10, borderWidth: 1, borderColor: '#E5E7EB' },
  itemHeader: { flexDirection: 'row', justifyContent: 'space-between' },
  itemPharmacy: { fontWeight: '600', color: '#374151' },
  itemDistance: { fontSize: 12, color: '#9CA3AF' },
  itemPrice: { fontSize: 16, fontWeight: 'bold', color: '#111827', marginTop: 4 },
  itemSubtext: { fontSize: 12, color: '#6B7280' }
});
