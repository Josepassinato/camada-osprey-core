import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { 
  DollarSign, 
  Loader2, 
  Save, 
  RefreshCw, 
  CheckCircle,
  AlertCircle,
  Package,
  TrendingUp,
  TrendingDown
} from 'lucide-react';
import { makeApiCall } from '@/utils/api';

interface Product {
  _id: string;
  visa_code: string;
  name: string;
  price: number;
  category: string;
  category_name: string;
  description: string;
  includes: string[];
  stripe_product_id?: string;
  stripe_price_id?: string;
  stripe_synced_at?: string;
  active: boolean;
  updated_at: string;
}

const AdminProductManagement = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState<string | null>(null);
  const [syncing, setSyncing] = useState<string | null>(null);
  const [editingPrices, setEditingPrices] = useState<Record<string, number>>({});
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);

  useEffect(() => {
    loadProducts();
  }, []);

  const loadProducts = async () => {
    setLoading(true);
    try {
      const data = await makeApiCall('/admin/products', 'GET');
      
      if (data.success) {
        setProducts(data.products);
        
        // Inicializar preços editáveis
        const prices: Record<string, number> = {};
        data.products.forEach((p: Product) => {
          prices[p.visa_code] = p.price;
        });
        setEditingPrices(prices);
      }
    } catch (error: any) {
      showMessage('error', error.message || 'Erro ao carregar produtos');
    } finally {
      setLoading(false);
    }
  };

  const handlePriceChange = (visaCode: string, value: string) => {
    const numValue = parseFloat(value);
    setEditingPrices(prev => ({
      ...prev,
      [visaCode]: isNaN(numValue) ? 0 : numValue
    }));
  };

  const updatePrice = async (visaCode: string) => {
    const newPrice = editingPrices[visaCode];
    
    if (!newPrice || newPrice <= 0) {
      showMessage('error', 'Preço inválido');
      return;
    }

    setSaving(visaCode);
    try {
      const data = await makeApiCall(`/admin/products/${visaCode}/price`, 'PUT', {
        price: newPrice,
        sync_stripe: true
      });

      if (data.success) {
        showMessage('success', `Preço atualizado: $${data.old_price} → $${data.new_price}`);
        await loadProducts(); // Recarregar lista
      } else {
        showMessage('error', data.error || 'Erro ao atualizar preço');
      }
    } catch (error: any) {
      showMessage('error', error.message || 'Erro ao atualizar preço');
    } finally {
      setSaving(null);
    }
  };

  const syncWithStripe = async (visaCode: string) => {
    setSyncing(visaCode);
    try {
      const data = await makeApiCall(`/admin/products/${visaCode}/sync-stripe`, 'POST');

      if (data.success) {
        showMessage('success', 'Produto sincronizado com Stripe!');
        await loadProducts();
      } else {
        showMessage('error', data.error || 'Erro ao sincronizar');
      }
    } catch (error: any) {
      showMessage('error', error.message || 'Erro ao sincronizar com Stripe');
    } finally {
      setSyncing(null);
    }
  };

  const syncAllWithStripe = async () => {
    setSyncing('all');
    try {
      const data = await makeApiCall('/admin/products/sync-all-stripe', 'POST');

      if (data.success) {
        showMessage('success', `${data.synced} produtos sincronizados com Stripe!`);
        await loadProducts();
      } else {
        showMessage('error', data.error || 'Erro ao sincronizar');
      }
    } catch (error: any) {
      showMessage('error', error.message || 'Erro ao sincronizar produtos');
    } finally {
      setSyncing(null);
    }
  };

  const showMessage = (type: 'success' | 'error', text: string) => {
    setMessage({ type, text });
    setTimeout(() => setMessage(null), 5000);
  };

  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      'basic': 'bg-blue-100 text-blue-800',
      'intermediate': 'bg-purple-100 text-purple-800',
      'advanced': 'bg-orange-100 text-orange-800',
      'premium': 'bg-pink-100 text-pink-800',
      'special': 'bg-green-100 text-green-800'
    };
    return colors[category] || 'bg-gray-100 text-gray-800';
  };

  const hasChanges = (visaCode: string) => {
    const product = products.find(p => p.visa_code === visaCode);
    return product && editingPrices[visaCode] !== product.price;
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-purple-600" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Gerenciamento de Produtos
          </h1>
          <p className="text-gray-600">
            Gerencie preços dos vistos e sincronize com o Stripe
          </p>
        </div>

        {/* Message */}
        {message && (
          <div className={`mb-6 p-4 rounded-lg ${
            message.type === 'success' 
              ? 'bg-green-50 border border-green-200' 
              : 'bg-red-50 border border-red-200'
          }`}>
            <div className="flex items-center gap-2">
              {message.type === 'success' ? (
                <CheckCircle className="h-5 w-5 text-green-600" />
              ) : (
                <AlertCircle className="h-5 w-5 text-red-600" />
              )}
              <p className={message.type === 'success' ? 'text-green-800' : 'text-red-800'}>
                {message.text}
              </p>
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="mb-6 flex gap-3">
          <Button
            onClick={syncAllWithStripe}
            disabled={syncing === 'all'}
            variant="outline"
            className="flex items-center gap-2"
          >
            {syncing === 'all' ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <RefreshCw className="h-4 w-4" />
            )}
            Sincronizar Todos com Stripe
          </Button>
          
          <Button
            onClick={loadProducts}
            variant="outline"
            className="flex items-center gap-2"
          >
            <RefreshCw className="h-4 w-4" />
            Recarregar
          </Button>
        </div>

        {/* Products Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {products.map((product) => (
            <Card key={product.visa_code} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <CardTitle className="text-lg">
                      {product.visa_code}
                    </CardTitle>
                    <p className="text-sm text-gray-600 mt-1">{product.name}</p>
                  </div>
                  <Badge className={getCategoryColor(product.category)}>
                    {product.category_name}
                  </Badge>
                </div>
                <CardDescription className="text-xs">
                  {product.description}
                </CardDescription>
              </CardHeader>

              <CardContent>
                {/* Current Price */}
                <div className="mb-4 p-3 bg-gray-50 rounded-lg">
                  <p className="text-xs text-gray-500 mb-1">Preço Atual</p>
                  <p className="text-2xl font-bold text-gray-900">
                    ${product.price.toFixed(2)}
                  </p>
                </div>

                {/* New Price Input */}
                <div className="mb-4">
                  <label className="text-xs text-gray-600 mb-2 block">
                    Novo Preço
                  </label>
                  <div className="flex gap-2">
                    <div className="relative flex-1">
                      <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                      <Input
                        type="number"
                        step="0.01"
                        min="0"
                        value={editingPrices[product.visa_code]}
                        onChange={(e) => handlePriceChange(product.visa_code, e.target.value)}
                        className="pl-9"
                      />
                    </div>
                  </div>
                  
                  {hasChanges(product.visa_code) && (
                    <div className="mt-2 flex items-center gap-1 text-xs">
                      {editingPrices[product.visa_code] > product.price ? (
                        <>
                          <TrendingUp className="h-3 w-3 text-red-600" />
                          <span className="text-red-600">
                            +${(editingPrices[product.visa_code] - product.price).toFixed(2)}
                          </span>
                        </>
                      ) : (
                        <>
                          <TrendingDown className="h-3 w-3 text-green-600" />
                          <span className="text-green-600">
                            -${(product.price - editingPrices[product.visa_code]).toFixed(2)}
                          </span>
                        </>
                      )}
                    </div>
                  )}
                </div>

                {/* Stripe Status */}
                <div className="mb-4 p-2 bg-blue-50 rounded text-xs">
                  <div className="flex items-center gap-1 mb-1">
                    <Package className="h-3 w-3 text-blue-600" />
                    <span className="font-medium text-blue-900">Status Stripe:</span>
                  </div>
                  {product.stripe_product_id ? (
                    <p className="text-blue-700">
                      ✓ Sincronizado
                      {product.stripe_synced_at && (
                        <span className="block text-blue-600 mt-1">
                          {new Date(product.stripe_synced_at).toLocaleString('pt-BR')}
                        </span>
                      )}
                    </p>
                  ) : (
                    <p className="text-amber-700">⚠ Não sincronizado</p>
                  )}
                </div>

                {/* Actions */}
                <div className="flex gap-2">
                  <Button
                    onClick={() => updatePrice(product.visa_code)}
                    disabled={saving === product.visa_code || !hasChanges(product.visa_code)}
                    className="flex-1 bg-purple-600 hover:bg-purple-700"
                    size="sm"
                  >
                    {saving === product.visa_code ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <>
                        <Save className="h-4 w-4 mr-1" />
                        Salvar
                      </>
                    )}
                  </Button>
                  
                  <Button
                    onClick={() => syncWithStripe(product.visa_code)}
                    disabled={syncing === product.visa_code}
                    variant="outline"
                    size="sm"
                  >
                    {syncing === product.visa_code ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <RefreshCw className="h-4 w-4" />
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
};

export default AdminProductManagement;
