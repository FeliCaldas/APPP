import streamlit as st
import sqlite3
import pandas as pd
import io
from database import (
    init_db, add_vehicle, get_vehicles, update_vehicle, delete_vehicle,
    add_maintenance, get_vehicle_maintenance, update_maintenance, delete_maintenance,
    get_all_maintenance_records
)
from fipe_api import get_fipe_brands, get_fipe_models, get_fipe_years, get_fipe_price
from vehicle_manager import save_image
import base64
from io import BytesIO
from datetime import datetime, timedelta

def main():
    # Configuração da página para mobile
    st.set_page_config(
        page_title="Gerenciador de Veículos",
        layout="wide",
        initial_sidebar_state="collapsed",
        menu_items={
            'About': 'Gerenciador de Veículos - Versão Mobile'
        }
    )
    
    # Configurações para melhor experiência mobile
    st.markdown("""
        <style>
        [data-testid="stSidebar"][aria-expanded="true"] {
            max-width: 80%;
            width: 80%;
        }
        .streamlit-expanderHeader {
            font-size: 1em;
        }
        .stButton > button {
            width: 100%;
            border-radius: 20px;
            height: 3em;
        }
        @media (max-width: 640px) {
            .main > div {
                padding-left: 0.5rem;
                padding-right: 0.5rem;
            }
        }
        </style>
    """, unsafe_allow_html=True)
    st._config.set_option('server.address', '0.0.0.0')

    # CSS para melhorar a interface mobile
    st.markdown("""
        <style>
        .stButton>button {
            width: 100%;
            height: 50px;
            margin: 5px 0;
        }
        .stSelectbox {
            margin: 10px 0;
        }
        .vehicle-info {
            font-size: 18px !important;
            line-height: 2 !important;
            padding: 10px 0;
        }
        .vehicle-info p {
            margin: 10px 0 !important;
        }
        .delete-button {
            background-color: #ff4b4b !important;
            color: white !important;
            border: none !important;
            padding: 0.5rem !important;
            border-radius: 0.3rem !important;
            cursor: pointer !important;
        }
        .maintenance-card {
            background-color: #f0f2f6;
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 0.5rem 0;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("Gerenciador de Veículos")
    init_db()

    # Menu mais amigável para mobile
    menu = st.selectbox(
        "Escolha uma opção",
        ["Adicionar Veículo", "Visualizar Veículos"]
    )

    if menu == "Adicionar Veículo":
        add_vehicle_form()
    else:
        view_vehicles()

def add_maintenance_form(vehicle_id, maintenance_data=None):
    is_editing = maintenance_data is not None

    with st.form(key=f"maintenance_form_{vehicle_id}"):
        st.subheader("Registrar Manutenção" if not is_editing else "Editar Manutenção")

        date = st.date_input(
            "Data da Manutenção",
            value=datetime.strptime(maintenance_data['date'], '%Y-%m-%d').date() if is_editing else datetime.now(),
            key=f"date_{vehicle_id}"
        )

        description = st.text_area(
            "Descrição do Serviço",
            value=maintenance_data['description'] if is_editing else "",
            key=f"description_{vehicle_id}"
        )

        cost = st.number_input(
            "Custo (R$)",
            value=maintenance_data['cost'] if is_editing else 0.0,
            min_value=0.0,
            step=10.0,
            format="%.2f",
            key=f"cost_{vehicle_id}"
        )

        mileage = st.number_input(
            "Quilometragem",
            value=maintenance_data['mileage'] if is_editing else 0,
            min_value=0,
            step=1000,
            key=f"mileage_{vehicle_id}"
        )

        next_date = st.date_input(
            "Próxima Manutenção",
            value=datetime.strptime(maintenance_data['next_maintenance_date'], '%Y-%m-%d').date() if is_editing and maintenance_data['next_maintenance_date'] else (datetime.now() + timedelta(days=180)).date(),
            key=f"next_date_{vehicle_id}"
        )

        submit_button = st.form_submit_button(
            "Atualizar Manutenção" if is_editing else "Registrar Manutenção"
        )

        if submit_button:
            maintenance_info = {
                'vehicle_id': vehicle_id,
                'date': date.strftime('%Y-%m-%d'),
                'description': description,
                'cost': cost,
                'mileage': mileage,
                'next_maintenance_date': next_date.strftime('%Y-%m-%d')
            }

            try:
                if is_editing:
                    update_maintenance(maintenance_data['id'], maintenance_info)
                    st.success("Manutenção atualizada com sucesso!")
                else:
                    add_maintenance(maintenance_info)
                    st.success("Manutenção registrada com sucesso!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao {'atualizar' if is_editing else 'registrar'} manutenção: {str(e)}")

def view_maintenance_history(vehicle_id):
    maintenance_records = get_vehicle_maintenance(vehicle_id)

    # Inicializa estados para manutenção se não existirem
    if 'editing_maintenance' not in st.session_state:
        st.session_state.editing_maintenance = None
    if 'delete_maintenance_confirmation' not in st.session_state:
        st.session_state.delete_maintenance_confirmation = {}
    if 'show_maintenance_form' not in st.session_state:
        st.session_state.show_maintenance_form = {}

    # Adicionar nova manutenção
    if st.button("➕ Nova Manutenção", key=f"new_maintenance_{vehicle_id}"):
        st.session_state.show_maintenance_form[vehicle_id] = True
        st.rerun()

    # Mostrar formulário de nova manutenção se necessário
    if st.session_state.show_maintenance_form.get(vehicle_id, False):
        st.subheader("Nova Manutenção")
        with st.form(key=f"maintenance_form_{vehicle_id}"):
            date = st.date_input(
                "Data da Manutenção",
                value=datetime.now(),
                key=f"date_{vehicle_id}"
            )

            description = st.text_area(
                "Descrição do Serviço",
                key=f"description_{vehicle_id}"
            )

            cost = st.number_input(
                "Custo (R$)",
                value=0.0,
                min_value=0.0,
                step=10.0,
                format="%.2f",
                key=f"cost_{vehicle_id}"
            )

            mileage = st.number_input(
                "Quilometragem",
                value=0,
                min_value=0,
                step=1000,
                key=f"mileage_{vehicle_id}"
            )

            submit = st.form_submit_button("Salvar Manutenção")

            if submit:
                try:
                    maintenance_info = {
                        'vehicle_id': vehicle_id,
                        'date': date.strftime('%Y-%m-%d'),
                        'description': description,
                        'cost': cost,
                        'mileage': mileage,
                        'next_maintenance_date': None
                    }
                    add_maintenance(maintenance_info)
                    st.success("Manutenção registrada com sucesso!")
                    st.session_state.show_maintenance_form[vehicle_id] = False
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao registrar manutenção: {str(e)}")

        if st.button("❌ Cancelar", key=f"cancel_maintenance_{vehicle_id}"):
            st.session_state.show_maintenance_form[vehicle_id] = False
            st.rerun()

    # Mostrar manutenções existentes
    if maintenance_records:
        for record in maintenance_records:
            with st.container():
                maintenance_info = f"""
                    <div class="maintenance-card">
                    <h4>📅 {record['date']}</h4>
                    <p><strong>Serviço:</strong> {record['description']}</p>
                    <p><strong>Custo:</strong> R$ {record['cost']:.2f}</p>
                    <p><strong>Quilometragem:</strong> {record['mileage']} km</p>
                    """

                maintenance_info += "</div>"

                st.markdown(maintenance_info, unsafe_allow_html=True)

                if st.button("🗑️ Excluir", key=f"delete_maintenance_{record['id']}", type="primary"):
                    st.session_state.delete_maintenance_confirmation[record['id']] = True

                if st.session_state.delete_maintenance_confirmation.get(record['id'], False):
                    if st.button("⚠️ Confirmar Exclusão", key=f"confirm_delete_maintenance_{record['id']}", type="primary"):
                        delete_maintenance(record['id'])
                        st.success("Manutenção excluída com sucesso!")
                        st.session_state.delete_maintenance_confirmation[record['id']] = False
                        st.rerun()
    else:
        st.info("Nenhuma manutenção registrada para este veículo.")

def add_vehicle_form(vehicle_data=None):
    is_editing = vehicle_data is not None
    st.header("Editar Veículo" if is_editing else "Adicionar Novo Veículo")

    # Interface mais touch-friendly
    with st.container():
        brands = get_fipe_brands()
        selected_brand = st.selectbox(
            "Marca do Veículo",
            options=brands['codigo'].tolist(),
            format_func=lambda x: brands[brands['codigo'] == x]['nome'].iloc[0],
            index=0 if not is_editing else next((i for i, row in brands.iterrows() if row['nome'] == vehicle_data['brand']), 0)
        )

        models = get_fipe_models(selected_brand)
        selected_model = st.selectbox(
            "Modelo do Veículo",
            options=models['codigo'].tolist(),
            format_func=lambda x: models[models['codigo'] == x]['nome'].iloc[0],
            index=0 if not is_editing else next((i for i, row in models.iterrows() if row['nome'] == vehicle_data['model']), 0)
        )

        years = get_fipe_years(selected_brand, selected_model)
        selected_year = st.selectbox(
            "Ano do Veículo",
            options=years['codigo'].tolist(),
            format_func=lambda x: years[years['codigo'] == x]['nome'].iloc[0],
            index=0 if not is_editing else next((i for i, row in years.iterrows() if row['nome'] == vehicle_data['year']), 0)
        )

        color = st.text_input(
            "Cor do Veículo",
            value=vehicle_data.get('color', '') if is_editing else ""
        )

        purchase_price = st.number_input(
            "Valor de Aquisição (R$)",
            min_value=0.0,
            step=100.0,
            format="%.2f",
            value=vehicle_data['purchase_price'] if is_editing else 0.0
        )

        additional_costs = st.number_input(
            "Custos Adicionais (R$)",
            min_value=0.0,
            step=100.0,
            format="%.2f",
            value=vehicle_data['additional_costs'] if is_editing else 0.0
        )

        uploaded_file = st.file_uploader(
            "Foto do Veículo (Toque para selecionar)",
            type=['jpg', 'jpeg', 'png']
        )

    button_text = "Salvar Alterações" if is_editing else "Salvar Veículo"
    if st.button(button_text, use_container_width=True):
        try:
            fipe_data = get_fipe_price(selected_brand, selected_model, selected_year)
            fipe_price = float(fipe_data['Valor'].replace('R$ ', '').replace('.', '').replace(',', '.'))

            # Mantém a imagem existente se não houver upload de nova imagem
            if is_editing:
                image_data = vehicle_data['image_data']
                if uploaded_file:
                    image_bytes = uploaded_file.getvalue()
                    image_data = base64.b64encode(image_bytes).decode()
            else:
                image_data = None
                if uploaded_file:
                    image_bytes = uploaded_file.getvalue()
                    image_data = base64.b64encode(image_bytes).decode()

            total_cost = purchase_price + additional_costs
            fipe_difference = fipe_price - total_cost

            vehicle_info = {
                'brand': brands[brands['codigo'] == selected_brand]['nome'].iloc[0],
                'model': models[models['codigo'] == selected_model]['nome'].iloc[0],
                'year': years[years['codigo'] == selected_year]['nome'].iloc[0],
                'color': color,
                'purchase_price': purchase_price,
                'additional_costs': additional_costs,
                'fipe_price': fipe_price,
                'image_data': image_data
            }

            if is_editing:
                update_vehicle(vehicle_data['id'], vehicle_info)
                st.success("Veículo atualizado com sucesso!")
                st.session_state.editing_vehicle = None  # Limpa o estado de edição
            else:
                add_vehicle(vehicle_info)
                st.success("Veículo adicionado com sucesso!")

            st.balloons()
            st.rerun()

        except Exception as e:
            st.error(f"Erro ao {'atualizar' if is_editing else 'salvar'} veículo: {str(e)}")

def export_maintenance_report():
    records = get_all_maintenance_records()
    if records:
        df = pd.DataFrame(records)
        df = df[[
            'date', 'brand', 'model', 'year', 'description',
            'cost', 'mileage'
        ]]
        df.columns = [
            'Data', 'Marca', 'Modelo', 'Ano', 'Descrição',
            'Custo', 'Quilometragem'
        ]
        
        csv = df.to_csv(index=False)
        
        st.download_button(
            label="📥 Exportar Relatório de Manutenções",
            data=csv,
            file_name="relatorio_manutencoes.csv",
            mime="text/csv"
        )
    else:
        st.info("Não há registros de manutenção para exportar.")

def view_vehicles():
    st.header("Veículos Cadastrados")
    
    # Botão de exportação no topo da página
    export_maintenance_report()

    vehicles = get_vehicles()

    # Inicializa os estados se não existirem
    if 'delete_confirmation' not in st.session_state:
        st.session_state.delete_confirmation = {}
    if 'editing_vehicle' not in st.session_state:
        st.session_state.editing_vehicle = None

    for vehicle in vehicles:
        with st.expander(f"{vehicle['brand']} {vehicle['model']} ({vehicle['year']})"):
            if st.session_state.editing_vehicle == vehicle['id']:
                add_vehicle_form(vehicle)
                if st.button("❌ Cancelar Edição", key=f"cancel_{vehicle['id']}", type="primary"):
                    st.session_state.editing_vehicle = None
                    st.rerun()
            else:
                if vehicle['image_data']:
                    image_bytes = base64.b64decode(vehicle['image_data'])
                    st.image(image_bytes, use_column_width=True)

                total_cost = vehicle['purchase_price'] + vehicle['additional_costs']
                difference = vehicle['fipe_price'] - total_cost

                st.markdown(f"""
                    <div class="vehicle-info">
                    <p>🎨 <strong>Cor:</strong> {vehicle.get('color', 'Não informada')}</p>
                    <p>📊 <strong>Valor de Aquisição:</strong> R$ {vehicle['purchase_price']:.2f}</p>
                    <p>💰 <strong>Custos Adicionais:</strong> R$ {vehicle['additional_costs']:.2f}</p>
                    <p>💵 <strong>Valor Total:</strong> R$ {total_cost:.2f}</p>
                    <p>🚗 <strong>Valor FIPE:</strong> R$ {vehicle['fipe_price']:.2f}</p>
                    <p>📈 <strong>Diferença FIPE:</strong> R$ {difference:.2f}</p>
                    </div>
                """, unsafe_allow_html=True)

                if difference > 0:
                    st.success("✅ Valor positivo em relação à FIPE")
                else:
                    st.error("❌ Valor negativo em relação à FIPE")

                # Adiciona seção de manutenções
                st.subheader("📝 Histórico de Manutenções")
                view_maintenance_history(vehicle['id'])

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✏️ Editar", key=f"edit_{vehicle['id']}", type="primary"):
                        st.session_state.editing_vehicle = vehicle['id']
                        st.rerun()

                with col2:
                    if st.button(f"🗑️ Excluir", key=f"delete_{vehicle['id']}", type="primary"):
                        st.session_state.delete_confirmation[vehicle['id']] = True

                    if st.session_state.delete_confirmation.get(vehicle['id'], False):
                        if st.button(f"⚠️ Confirmar Exclusão", key=f"confirm_{vehicle['id']}", type="primary"):
                            delete_vehicle(vehicle['id'])
                            st.success("Veículo excluído com sucesso!")
                            st.session_state.delete_confirmation[vehicle['id']] = False
                            st.rerun()

if __name__ == "__main__":
    main()